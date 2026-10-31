#!/usr/bin/env python3
"""Generate Vietnamese Office/PDF coursework deliverables from project evidence."""

from __future__ import annotations

import html
import re
import shutil
import zipfile
from collections import Counter
from pathlib import Path
from typing import Iterable

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from openpyxl import Workbook, load_workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo
from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image as PdfImage,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table as PdfTable,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TEAM = ROOT / "Team"
EVIDENCE = TEAM / "7. Evidence"
RUN_ID = "MC-20261031-100139"
ALLOWED_STATUSES = ("PASS", "FAIL", "BLOCKED", "NOT EXECUTED")

FUNCTION_BY_REQUIREMENT = {
    "REQ-001": ("F-01", "Trang chủ và điều hướng"),
    "REQ-002": ("F-02", "Danh mục và thẻ sản phẩm"),
    "REQ-003": ("F-04", "Tìm kiếm sản phẩm"),
    "REQ-004": ("F-03", "Sắp xếp danh sách"),
    "REQ-005": ("F-05", "Chi tiết sản phẩm"),
    "REQ-006": ("F-08", "Giỏ hàng"),
    "REQ-007": ("F-06, F-07", "Đăng nhập và đăng ký"),
    "REQ-008": ("F-09", "Tra cứu bảo hành"),
}

REQUIREMENTS = {
    "REQ-001": "Trang chủ tải và điều hướng người dùng tới các chức năng/danh mục công khai.",
    "REQ-002": "Danh mục hiển thị thẻ sản phẩm có tên và giá khi giá được công bố.",
    "REQ-003": "Người dùng gửi từ khóa tìm kiếm; kết quả phù hợp hoặc trạng thái rỗng được hiển thị.",
    "REQ-004": "Người dùng chọn sắp xếp danh sách theo giá tăng dần hoặc giảm dần.",
    "REQ-005": "Trang chi tiết tương ứng sản phẩm đã chọn và hiển thị thông tin công khai.",
    "REQ-006": "Người dùng cập nhật số lượng giỏ và xác minh giá trị được lưu sau reload.",
    "REQ-007": "Giao diện đăng nhập/đăng ký khả dụng; không xác thực hoặc gửi OTP trái phép.",
    "REQ-008": "Form tra cứu bảo hành dùng dữ liệu được ủy quyền và hiển thị trạng thái phù hợp.",
}

STATUS_FILL = {
    "PASS": "C6EFCE",
    "FAIL": "FFC7CE",
    "BLOCKED": "FCE4D6",
    "NOT EXECUTED": "E7E6E6",
}
STATUS_FONT = {
    "PASS": "006100",
    "FAIL": "9C0006",
    "BLOCKED": "9C6500",
    "NOT EXECUTED": "666666",
}


def markdown_text(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("**", "").replace("__", "")
    value = value.replace("`", "").replace("*", "")
    return html.unescape(value).strip()


def table_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def markdown_tables(path: Path) -> list[tuple[list[str], list[list[str]]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    tables: list[tuple[list[str], list[list[str]]]] = []
    index = 0
    while index + 1 < len(lines):
        if not lines[index].lstrip().startswith("|"):
            index += 1
            continue
        header = table_cells(lines[index])
        if not re.fullmatch(r"\|?[\s:|-]+\|?", lines[index + 1].strip()):
            index += 1
            continue
        rows: list[list[str]] = []
        index += 2
        while index < len(lines) and lines[index].lstrip().startswith("|"):
            row = table_cells(lines[index])
            if len(row) == len(header):
                rows.append(row)
            index += 1
        tables.append((header, rows))
    return tables


def find_table(path: Path, first_header: str, required_headers: Iterable[str] = ()) -> tuple[list[str], list[list[str]]]:
    required = set(required_headers)
    for header, rows in markdown_tables(path):
        if header and header[0] == first_header and required.issubset(set(header)):
            return header, rows
    raise ValueError(f"Markdown table not found in {path.name}: {first_header}")


def header_index(header: list[str], name: str) -> int:
    try:
        return header.index(name)
    except ValueError as exc:
        raise ValueError(f"Missing column {name!r} in table header {header}") from exc


def normalized_rows(
    header: list[str], rows: list[list[str]], status_column: str = "Status"
) -> list[dict[str, str]]:
    result = []
    for row in rows:
        item = {key: markdown_text(row[index]) for index, key in enumerate(header)}
        if status_column in item and item[status_column] not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid test status {item[status_column]!r}")
        result.append(item)
    return result


def load_cases() -> dict[str, list[dict[str, str]]]:
    bb_header, bb_rows = find_table(DOCS / "black-box-test-cases.md", "Test Case ID")
    _, unit_design_rows = find_table(
        DOCS / "unit-testing.md", "Unit Test ID", ("Điều kiện kiểm tra",)
    )
    unit_result_header, unit_result_rows = find_table(
        DOCS / "unit-testing.md", "Unit Test ID", ("Actual Result", "Status")
    )
    _, integration_rows = find_table(
        DOCS / "integration-testing.md", "Test ID", ("Điểm tích hợp", "Trạng thái")
    )
    _, system_rows = find_table(
        DOCS / "system-testing.md", "Test ID", ("Mục tiêu", "Trạng thái")
    )

    unit_design_header, _ = find_table(
        DOCS / "unit-testing.md", "Unit Test ID", ("Điều kiện kiểm tra",)
    )
    actual_index = header_index(unit_result_header, "Actual Result")
    result_status_index = header_index(unit_result_header, "Status")
    unit_results = {
        row[0]: (markdown_text(row[actual_index]), markdown_text(row[result_status_index]))
        for row in unit_result_rows
    }

    unit_cases = []
    for row in unit_design_rows:
        item = {key: markdown_text(row[index]) for index, key in enumerate(unit_design_header)}
        actual, status = unit_results[item["Unit Test ID"]]
        item["Actual Result"] = actual
        item["Status"] = status
        unit_cases.append(item)
    unit_cases.extend(
        [
            {
                "Unit Test ID": "UT-EVIDENCE-01",
                "Phương thức": "writesVietnameseEvidenceAsUtf8",
                "Điều kiện kiểm tra": "UTF-8 tiếng Việt được ghi nguyên vẹn vào log.",
                "Nhánh/đường đi": "Ghi log thành công; đọc lại file UTF-8.",
                "Kết quả mong đợi": "Nội dung tiếng Việt còn nguyên; không có ký tự thay thế.",
                "Actual Result": "Surefire PASS; run MC-20261031-100139.",
                "Status": "PASS",
            },
            {
                "Unit Test ID": "UT-EVIDENCE-02",
                "Phương thức": "redactsCredentialLikeValuesFromEvidence",
                "Điều kiện kiểm tra": "Giá trị giống credentials/token được lọc khỏi log.",
                "Nhánh/đường đi": "Ghi chuỗi nhạy cảm thử nghiệm; xác nhận chỉ còn marker redaction.",
                "Kết quả mong đợi": "Giá trị đầu vào không xuất hiện trong log.",
                "Actual Result": "Surefire PASS; run MC-20261031-100139.",
                "Status": "PASS",
            },
        ]
    )

    return {
        "BlackBox": normalized_rows(bb_header, bb_rows),
        "Unit": unit_cases,
        "Integration": normalized_rows(
            ["Test ID", "Điểm tích hợp", "Thành phần", "Dữ liệu đầu vào",
             "Các bước", "Kết quả mong đợi", "Kết quả thực tế", "Trạng thái"],
            integration_rows,
            "Trạng thái",
        ),
        "System": normalized_rows(
            ["Test ID", "Mục tiêu", "Điều kiện tiền đề", "Dữ liệu kiểm thử",
             "Các bước", "Kết quả mong đợi", "Kết quả thực tế", "Trạng thái"],
            system_rows,
            "Trạng thái",
        ),
    }


def case_status_counts(cases: list[dict[str, str]], key: str = "Status") -> Counter[str]:
    counts = Counter({status: 0 for status in ALLOWED_STATUSES})
    for case in cases:
        status_column = key if key in case else "Trạng thái"
        status = case[status_column]
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        counts[status] += 1
    return counts


def set_cell_fill(cell, color: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color)
    properties.append(shading)


def set_cell_margins(cell, top=70, start=90, bottom=70, end=90) -> None:
    properties = cell._tc.get_or_add_tcPr()
    margins = properties.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        properties.append(margins)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = margins.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            margins.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def configure_docx(document: Document, landscape: bool = False) -> None:
    for section in document.sections:
        section.top_margin = Inches(0.65)
        section.bottom_margin = Inches(0.65)
        section.left_margin = Inches(0.72)
        section.right_margin = Inches(0.72)
        if landscape:
            section.orientation = WD_ORIENT.LANDSCAPE
            section.page_width, section.page_height = section.page_height, section.page_width
    normal = document.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(9.5)
    normal.font.color.rgb = RGBColor(38, 50, 56)
    for style_name, size, color in (
        ("Title", 24, "17365D"),
        ("Heading 1", 16, "17365D"),
        ("Heading 2", 12, "1F4E79"),
        ("Heading 3", 10, "365F91"),
    ):
        style = document.styles[style_name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
    for section in document.sections:
        footer = section.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.add_run("MobileCity Testing | IT6084 — Trang ")
        field = OxmlElement("w:fldSimple")
        field.set(qn("w:instr"), "PAGE")
        footer._p.append(field)


def add_cover(document: Document, title: str, subtitle: str) -> None:
    p = document.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(80)
    run = p.add_run("MOBILECITY")
    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(195, 146, 34)

    p = document.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(18)
    p.add_run(title)

    p = document.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(subtitle)
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(74, 85, 104)
    document.add_paragraph()
    info = document.add_table(rows=3, cols=2)
    info.style = "Light Shading Accent 1"
    for row, values in zip(
        info.rows,
        [
            ("Học phần", "Kiểm thử phần mềm — IT6084"),
            ("Website", "https://mobilecity.vn/"),
            ("Baseline", f"{RUN_ID} | 31/10/2026 | Windows / Java 17 / Chrome"),
        ],
    ):
        for cell, value in zip(row.cells, values):
            cell.text = value
            set_cell_margins(cell)
    document.add_page_break()


def plain_cell_text(value: str) -> str:
    return markdown_text(value).replace("<br>", "\n")


def add_word_table(document: Document, headers: list[str], rows: list[list[str]]) -> None:
    if not headers:
        return
    table = document.add_table(rows=1, cols=len(headers))
    table.style = "Light Shading Accent 1"
    table.autofit = True
    header_cells = table.rows[0].cells
    for cell, text in zip(header_cells, headers):
        cell.text = plain_cell_text(text)
        set_cell_fill(cell, "17365D")
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
                run.font.size = Pt(8)
    for row in rows:
        cells = table.add_row().cells
        for index, cell in enumerate(cells):
            value = plain_cell_text(row[index]) if index < len(row) else ""
            cell.text = value
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run.font.size = Pt(7.5 if len(headers) > 5 else 8.5)
            if headers[index].lower() in ("status", "trạng thái") and value in STATUS_FILL:
                set_cell_fill(cell, STATUS_FILL[value])
    table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))


def add_markdown_body(document: Document, path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    headings: list[str] = []
    index = 0
    skipped_first_title = False
    while index < len(lines):
        line = lines[index]
        if not line.strip():
            index += 1
            continue
        if line.startswith("```"):
            code_lines = []
            index += 1
            while index < len(lines) and not lines[index].startswith("```"):
                code_lines.append(lines[index])
                index += 1
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.left_indent = Inches(0.18)
            paragraph.paragraph_format.space_after = Pt(5)
            run = paragraph.add_run("\n".join(code_lines))
            run.font.name = "Consolas"
            run.font.size = Pt(8)
            index += 1
            continue
        if line.lstrip().startswith("|") and index + 1 < len(lines) and re.fullmatch(
            r"\|?[\s:|-]+\|?", lines[index + 1].strip()
        ):
            headers = table_cells(line)
            rows = []
            index += 2
            while index < len(lines) and lines[index].lstrip().startswith("|"):
                row = table_cells(lines[index])
                if len(row) == len(headers):
                    rows.append(row)
                index += 1
            add_word_table(document, headers, rows)
            document.add_paragraph()
            continue
        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            text = markdown_text(heading.group(2))
            if not skipped_first_title and len(heading.group(1)) == 1:
                skipped_first_title = True
            else:
                level = min(len(heading.group(1)), 3)
                document.add_heading(text, level=level)
                if level <= 2:
                    headings.append(text)
            index += 1
            continue
        if line.startswith(">"):
            paragraph = document.add_paragraph(style="Quote")
            paragraph.add_run(markdown_text(line.lstrip("> ")))
            index += 1
            continue
        bullet = re.match(r"^\s*[-*]\s+(.+)$", line)
        numbered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if bullet or numbered:
            paragraph = document.add_paragraph(
                style="List Bullet" if bullet else "List Number"
            )
            paragraph.add_run(markdown_text((bullet or numbered).group(1)))
            index += 1
            continue
        paragraph_lines = [line.strip()]
        index += 1
        while index < len(lines):
            following = lines[index]
            if (
                not following.strip()
                or following.startswith("#")
                or following.startswith("```")
                or following.lstrip().startswith("|")
                or following.startswith(">")
                or re.match(r"^\s*(?:[-*]\s+|\d+\.\s+)", following)
            ):
                break
            paragraph_lines.append(following.strip())
            index += 1
        document.add_paragraph(markdown_text(" ".join(paragraph_lines)))
    return headings


def create_document_from_markdown(
    output: Path, title: str, subtitle: str, sources: list[Path], landscape: bool = False
) -> None:
    document = Document()
    configure_docx(document, landscape)
    add_cover(document, title, subtitle)
    document.add_heading("Mục lục", level=1)
    heading_index = []
    for source in sources:
        for line in source.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^#{1,2}\s+(.+)$", line)
            if match:
                heading_index.append(markdown_text(match.group(1)))
    for heading in heading_index:
        document.add_paragraph(heading, style="List Bullet")
    document.add_page_break()
    for source_index, source in enumerate(sources):
        if len(sources) > 1:
            document.add_heading(source.stem.replace("-", " ").title(), level=1)
        add_markdown_body(document, source)
        if source_index < len(sources) - 1:
            document.add_page_break()
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def add_summary_docx(output: Path, cases: dict[str, list[dict[str, str]]]) -> None:
    document = Document()
    configure_docx(document)
    add_cover(document, "BÁO CÁO TỔNG KẾT", "Kết quả kiểm thử phần mềm MobileCity")
    document.add_heading("1. Tóm tắt điều hành", level=1)
    document.add_paragraph(
        "Baseline Maven chạy trên website công khai MobileCity bằng Selenium và JUnit. "
        "Các kết quả chỉ áp dụng cho lần chạy và phạm vi kiểm thử được ghi dưới đây; "
        "không suy rộng thành kết luận chất lượng toàn website hoặc backend."
    )
    summary = [
        ("JUnit tests trong full suite", "33"),
        ("PASS / FAIL / BLOCKED", "32 / 0 / 1"),
        ("Lý do BLOCKED", "Thiếu credentials thử nghiệm được ủy quyền; giỏ hàng không bị thay đổi."),
        ("JaCoCo — TestConfig", "92.0% instructions; 94.6% lines; 73.1% branches."),
        ("Defect được xác nhận", "0"),
        ("Run ID", RUN_ID),
    ]
    add_word_table(document, ["Chỉ số", "Kết quả"], [list(row) for row in summary])

    document.add_heading("2. Thiết kế và trạng thái test case", level=1)
    category_rows = []
    for category, label in (
        ("BlackBox", "Hộp đen"),
        ("Unit", "Unit"),
        ("Integration", "Tích hợp"),
        ("System", "Hệ thống"),
    ):
        counts = case_status_counts(cases[category])
        category_rows.append(
            [
                label,
                str(len(cases[category])),
                str(counts["PASS"]),
                str(counts["FAIL"]),
                str(counts["BLOCKED"]),
                str(counts["NOT EXECUTED"]),
            ]
        )
    add_word_table(
        document,
        ["Nhóm", "Thiết kế", "PASS", "FAIL", "BLOCKED", "NOT EXECUTED"],
        category_rows,
    )
    document.add_heading("3. Các luồng hệ thống đã chạy", level=1)
    for item in (
        "SYS-001 — tìm kiếm Samsung, mở kết quả và xác nhận trang chi tiết.",
        "SYS-002 — từ khóa không khớp hiển thị trạng thái không có kết quả.",
        "SYS-003 — tải lại trang chi tiết và xác nhận cùng sản phẩm/giá.",
    ):
        document.add_paragraph(item, style="List Bullet")
    document.add_paragraph(
        "Ba luồng có ảnh chụp màn hình theo run ID. SYS-004 kiểm tra giỏ hàng là "
        "NOT EXECUTED vì thiếu tài khoản thử nghiệm được cấp phép."
    )

    document.add_heading("4. Defect và giới hạn", level=1)
    document.add_paragraph(
        "Không có defect được xác nhận trong các case đã chạy. Chưa kiểm thử sắp xếp, "
        "đăng ký, bảo hành, thanh toán/đặt hàng thật, lỗi server, timeout có kiểm soát "
        "hoặc tích hợp backend. Website không cung cấp mã nguồn nội bộ cho dự án này."
    )
    document.add_heading("5. Bằng chứng", level=1)
    for evidence in (
        "Surefire XML/text: Team/7. Evidence/… và target/surefire-reports/.",
        "JaCoCo HTML/XML/CSV: target/site/jacoco/.",
        "Log chạy: reports/test-execution.log.",
        "Ảnh hệ thống: screenshots/MC-20261031-100139-SYS-*.png.",
        "Phân tích, thiết kế và giới hạn: docs/*.md.",
    ):
        document.add_paragraph(evidence, style="List Bullet")
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def style_excel_sheet(ws, header_row: int, data_start: int, status_column: int | None = None) -> None:
    ws.freeze_panes = f"A{data_start}"
    ws.sheet_view.showGridLines = False
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.outlinePr.summaryBelow = True
    for cell in ws[header_row]:
        if cell.column <= ws.max_column:
            cell.fill = PatternFill("solid", fgColor="17365D")
            cell.font = Font(name="Arial", color="FFFFFF", bold=True, size=10)
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = Border(bottom=Side(style="medium", color="C39222"))
    ws.row_dimensions[header_row].height = 32
    for row in ws.iter_rows(min_row=data_start, max_row=ws.max_row):
        for cell in row:
            cell.font = Font(name="Arial", size=9, color="263238")
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        ws.row_dimensions[row[0].row].height = 45

    if status_column is not None and ws.max_row >= data_start:
        letter = ws.cell(header_row, status_column).column_letter
        validation = DataValidation(
            type="list",
            formula1='"PASS,FAIL,BLOCKED,NOT EXECUTED"',
            allow_blank=False,
        )
        validation.error = "Chỉ dùng PASS, FAIL, BLOCKED hoặc NOT EXECUTED."
        validation.errorTitle = "Trạng thái không hợp lệ"
        ws.add_data_validation(validation)
        validation.add(f"{letter}{data_start}:{letter}1000")
        for status, fill in STATUS_FILL.items():
            rule = FormulaRule(
                formula=[f'{letter}{data_start}="{status}"'],
                fill=PatternFill("solid", fgColor=fill),
                font=Font(color=STATUS_FONT[status], bold=True),
            )
            ws.conditional_formatting.add(f"{letter}{data_start}:{letter}1000", rule)


def write_case_sheet(
    ws,
    title: str,
    run_note: str,
    headers: list[str],
    rows: list[list[str]],
    status_header: str = "Status",
) -> None:
    last_col = max(1, len(headers))
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
    ws.cell(1, 1, title).font = Font(name="Arial", size=16, bold=True, color="17365D")
    ws.cell(1, 1).alignment = Alignment(vertical="center")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
    ws.cell(2, 1, run_note).font = Font(name="Arial", size=9, italic=True, color="666666")
    header_row = 4
    for column, header in enumerate(headers, 1):
        ws.cell(header_row, column, header)
    for row_index, row in enumerate(rows, header_row + 1):
        for column, value in enumerate(row, 1):
            cell = ws.cell(row_index, column, value)
            if headers[column - 1] == status_header:
                if value not in ALLOWED_STATUSES:
                    raise ValueError(f"Status column contains unsupported value {value!r}")
                cell.fill = PatternFill("solid", fgColor=STATUS_FILL[value])
                cell.font = Font(name="Arial", size=9, bold=True, color=STATUS_FONT[value])
    reference = f"A{header_row}:{ws.cell(max(header_row, ws.max_row), last_col).coordinate}"
    table = Table(displayName=re.sub(r"[^A-Za-z0-9]", "", ws.title) + "Cases", ref=reference)
    table.tableStyleInfo = TableStyleInfo(
        name="TableStyleMedium2", showFirstColumn=False, showLastColumn=False,
        showRowStripes=True, showColumnStripes=False,
    )
    ws.add_table(table)
    status_column = headers.index(status_header) + 1 if status_header in headers else None
    style_excel_sheet(ws, header_row, header_row + 1, status_column)
    width_limits = {
        "Test Case ID": 18, "Unit Test ID": 18, "Requirement ID": 16,
        "Status": 17, "Trạng thái": 17, "Technique": 30, "Test Objective": 38,
        "Test Objective ": 38, "Test ID": 16, "Mục tiêu": 38,
        "Actual Result": 45, "Kết quả thực tế": 45, "Các bước": 58,
        "Test Steps": 58, "Steps": 58, "Preconditions": 42,
        "Điều kiện tiền đề": 42, "Test Data": 32, "Dữ liệu kiểm thử": 32,
        "Expected Result": 46, "Kết quả mong đợi": 46,
        "Điểm tích hợp": 24, "Thành phần": 38, "Dữ liệu đầu vào": 28,
        "Phương thức": 40, "Điều kiện kiểm tra": 48, "Nhánh/đường đi": 44,
        "Kết quả mong đợi": 46,
    }
    for column, header in enumerate(headers, 1):
        ws.column_dimensions[ws.cell(header_row, column).column_letter].width = (
            width_limits.get(header, 24)
        )
    ws.auto_filter.ref = reference


def create_test_cases_workbook(cases: dict[str, list[dict[str, str]]]) -> Path:
    path = TEAM / "2. TestCases.xlsx"
    workbook = Workbook()
    overview = workbook.active
    overview.title = "Summary"
    overview.sheet_view.showGridLines = False
    overview.merge_cells("A1:F1")
    overview["A1"] = "MOBILECITY — TEST CASES & EXECUTION SUMMARY"
    overview["A1"].font = Font(name="Arial", size=16, bold=True, color="17365D")
    overview["A2"] = f"Baseline {RUN_ID} | Maven clean verify | 31/10/2026"
    overview["A4"], overview["B4"] = "Maven suite", "33 tests"
    overview["A5"], overview["B5"] = "PASS / FAIL / BLOCKED", "32 / 0 / 1"
    overview["A6"], overview["B6"] = "Build", "BUILD SUCCESS"
    overview["A8"], overview["B8"], overview["C8"], overview["D8"], overview["E8"], overview["F8"] = (
        "Nhóm", "Thiết kế", "PASS", "FAIL", "BLOCKED", "NOT EXECUTED"
    )
    for cell in overview[8]:
        cell.fill = PatternFill("solid", fgColor="17365D")
        cell.font = Font(name="Arial", color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
    labels = {"BlackBox": "Hộp đen", "Unit": "Unit", "Integration": "Tích hợp", "System": "Hệ thống"}
    for row_index, key in enumerate(("BlackBox", "Unit", "Integration", "System"), 9):
        counts = case_status_counts(cases[key])
        values = [labels[key], len(cases[key])] + [counts[status] for status in ALLOWED_STATUSES]
        for column, value in enumerate(values, 1):
            overview.cell(row_index, column, value)
            overview.cell(row_index, column).alignment = Alignment(vertical="top", wrap_text=True)
    overview["A15"] = "Quy ước"
    overview["A15"].font = Font(bold=True, color="17365D")
    overview["A16"] = "Chỉ sử dụng trạng thái PASS, FAIL, BLOCKED, NOT EXECUTED."
    overview["A17"] = "Các sheet test case chứa expected/actual, mã yêu cầu, bước chạy và kỹ thuật."
    overview["A18"] = "Một test Selenium có thể đồng thời là bằng chứng cho hơn một loại thiết kế."
    for column, width in {"A": 34, "B": 22, "C": 20, "D": 20, "E": 20, "F": 24}.items():
        overview.column_dimensions[column].width = width
    overview.freeze_panes = "A8"

    bb_headers = [
        "Test Case ID", "Requirement ID", "Test Objective", "Preconditions",
        "Test Data", "Test Steps", "Expected Result", "Actual Result", "Status", "Technique",
    ]
    bb_rows = [
        [case.get(header, "") for header in bb_headers] for case in cases["BlackBox"]
    ]
    write_case_sheet(
        workbook.create_sheet("BlackBox"), "Black-box test design", f"21 designed cases | Baseline {RUN_ID}",
        bb_headers, bb_rows,
    )

    unit_headers = [
        "Unit Test ID", "Phương thức", "Điều kiện kiểm tra", "Nhánh/đường đi",
        "Kết quả mong đợi", "Actual Result", "Status",
    ]
    unit_rows = [[case.get(header, "") for header in unit_headers] for case in cases["Unit"]]
    write_case_sheet(
        workbook.create_sheet("Unit"), "JUnit 5 unit tests", f"18 unit tests | JaCoCo scope: TestConfig | {RUN_ID}",
        unit_headers, unit_rows,
    )

    integration_headers = [
        "Test ID", "Điểm tích hợp", "Thành phần", "Dữ liệu đầu vào", "Các bước",
        "Kết quả mong đợi", "Kết quả thực tế", "Trạng thái",
    ]
    integration_rows = [[case.get(header, "") for header in integration_headers] for case in cases["Integration"]]
    write_case_sheet(
        workbook.create_sheet("Integration"), "Integration tests", f"7 designed cases; UI-observable integration only | {RUN_ID}",
        integration_headers, integration_rows, "Trạng thái",
    )

    system_headers = [
        "Test ID", "Mục tiêu", "Điều kiện tiền đề", "Dữ liệu kiểm thử", "Các bước",
        "Kết quả mong đợi", "Kết quả thực tế", "Trạng thái",
    ]
    system_rows = [[case.get(header, "") for header in system_headers] for case in cases["System"]]
    write_case_sheet(
        workbook.create_sheet("System"), "System test scenarios", f"4 designed scenarios; 3 executed | {RUN_ID}",
        system_headers, system_rows, "Trạng thái",
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)
    return path


def blackbox_code_reference(case_id: str) -> str:
    mappings = {
        "BB-HOME-01": "TC-HOME-001 / HomeTest.homepageLoadsWithTitle",
        "BB-HOME-02": "TC-HOME-002 / HomeTest.homepageOpensPhoneCategory",
        "BB-CAT-01": "TC-HOME-003 / ProductTest.categoryShowsNamedProduct",
        "BB-SEARCH-01": "TC-SEARCH-002 / SearchTest.searchReturnsMatchingProducts",
        "BB-SEARCH-02": "TC-SEARCH-003 / SearchTest.searchShowsEmptyStateForNoMatch",
        "BB-SEARCH-03": "TC-SEARCH-001 / SearchTest.emptySearchInputIsRequired",
        "BB-PRODUCT-01": "TC-PRODUCT-001 / ProductTest.listedProductOpensMatchingDetailPage",
        "BB-PRODUCT-02": "TC-PRODUCT-002/003/004 / ProductTest",
        "BB-CART-01": "TC-CART-001 / CartTest.loginAndTemporarilyChangeFirstCartItemQuantity",
    }
    return mappings.get(case_id, "Chưa có automated test tương ứng.")


def create_traceability_workbook(cases: dict[str, list[dict[str, str]]]) -> Path:
    path = TEAM / "6. Documentation" / "TraceabilityMatrix.xlsx"
    workbook = Workbook()
    requirements_ws = workbook.active
    requirements_ws.title = "Requirements"

    bb = {case["Test Case ID"]: case for case in cases["BlackBox"]}
    integ = {case["Test ID"]: case for case in cases["Integration"]}
    system = {case["Test ID"]: case for case in cases["System"]}

    bb_function = {
        "BB-HOME-01": "F-01", "BB-HOME-02": "F-01", "BB-CAT-01": "F-02",
        "BB-SORT-01": "F-03", "BB-SORT-02": "F-03",
        "BB-SEARCH-01": "F-04", "BB-SEARCH-02": "F-04", "BB-SEARCH-03": "F-04",
        "BB-PRODUCT-01": "F-05", "BB-PRODUCT-02": "F-05",
        "BB-ACCOUNT-01": "F-06", "BB-ACCOUNT-02": "F-07",
    }
    for case_id in bb:
        if case_id.startswith("BB-CART-"):
            bb_function[case_id] = "F-08"
        if case_id.startswith("BB-WARRANTY-"):
            bb_function[case_id] = "F-09"

    trace_rows: list[list[str]] = []
    for case_id, case in bb.items():
        req = case["Requirement ID"]
        trace_rows.append(
            [req, bb_function[case_id], case_id, blackbox_code_reference(case_id),
             "Black-box", case["Status"], case["Actual Result"]]
        )

    integration_map = {
        "IT-01": [("REQ-003", "F-04"), ("REQ-005", "F-05")],
        "IT-02": [("REQ-002", "F-02"), ("REQ-005", "F-05")],
        "IT-03": [("REQ-003", "F-04")],
        "IT-04": [("REQ-003", "F-04")],
        "IT-05": [("REQ-005", "F-05")],
        "IT-06": [("REQ-003", "F-04")],
        "IT-07": [("REQ-003", "F-04"), ("REQ-005", "F-05")],
    }
    integration_sources = {
        "IT-01": "TC-SEARCH-004 / SearchTest.searchResultOpensProductDetails",
        "IT-02": "TC-PRODUCT-001 / ProductTest.listedProductOpensMatchingDetailPage",
        "IT-03": "TC-SEARCH-001 / SearchTest.emptySearchInputIsRequired",
        "IT-04": "TC-SEARCH-003 / SearchTest.searchShowsEmptyStateForNoMatch",
        "IT-05": "No controlled fixture",
        "IT-06": "No authorized stub/API",
        "IT-07": "No controlled delay environment",
    }
    for case_id, req_functions in integration_map.items():
        case = integ[case_id]
        for req, function_id in req_functions:
            trace_rows.append(
                [req, function_id, case_id, integration_sources[case_id], "Integration",
                 case["Trạng thái"], case["Kết quả thực tế"]]
            )

    system_map = {
        "SYS-001": [("REQ-003", "F-04"), ("REQ-005", "F-05")],
        "SYS-002": [("REQ-003", "F-04")],
        "SYS-003": [("REQ-005", "F-05")],
        "SYS-004": [("REQ-006", "F-08")],
    }
    system_sources = {
        "SYS-001": "SystemTest.searchAndOpenMatchingProductDetails",
        "SYS-002": "SystemTest.unknownSearchTermShowsEmptyState",
        "SYS-003": "SystemTest.productDetailsRemainAvailableAfterReload",
        "SYS-004": "No execution; authorized account required",
    }
    for case_id, req_functions in system_map.items():
        case = system[case_id]
        for req, function_id in req_functions:
            trace_rows.append(
                [req, function_id, case_id, system_sources[case_id], "System",
                 case["Trạng thái"], case["Kết quả thực tế"]]
            )

    req_headers = [
        "Requirement ID", "Function ID", "Requirement Summary",
        "Linked Test Case IDs", "Coverage Status", "Evidence / Note",
    ]
    req_rows = []
    req_to_cases: dict[str, list[str]] = {req: [] for req in REQUIREMENTS}
    for row in trace_rows:
        req_to_cases[row[0]].append(row[2])
    for req, summary in REQUIREMENTS.items():
        related = [row for row in trace_rows if row[0] == req]
        statuses = {row[5] for row in related}
        if "FAIL" in statuses:
            overall = "FAIL"
        elif "BLOCKED" in statuses:
            overall = "BLOCKED"
        elif "PASS" in statuses:
            overall = "PASS"
        else:
            overall = "NOT EXECUTED"
        functions = FUNCTION_BY_REQUIREMENT[req][0]
        linked_ids = ", ".join(dict.fromkeys(req_to_cases[req]))
        note = {
            "REQ-001": "Homepage suite passed.",
            "REQ-002": "Category and product navigation passed.",
            "REQ-003": "Some search cases passed; additional input/boundary cases remain unexecuted.",
            "REQ-004": "Sort automation has not been implemented.",
            "REQ-005": "Public detail checks passed; negative integration cases remain unexecuted.",
            "REQ-006": "Cart test blocked before credential entry or mutation.",
            "REQ-007": "Login/register were not tested independently.",
            "REQ-008": "Authorized warranty data was unavailable.",
        }[req]
        req_rows.append([req, functions, summary, linked_ids, overall, note])

    write_case_sheet(
        requirements_ws,
        "Requirement → Function → Test Case",
        f"Traceability baseline {RUN_ID}; rollup precedence: FAIL, BLOCKED, PASS, NOT EXECUTED. "
        "Individual case statuses remain in Test Trace.",
        req_headers, req_rows, "Coverage Status",
    )
    requirements_ws.column_dimensions["A"].width = 18
    requirements_ws.column_dimensions["B"].width = 18
    requirements_ws.column_dimensions["C"].width = 68
    requirements_ws.column_dimensions["D"].width = 48
    requirements_ws.column_dimensions["E"].width = 20
    requirements_ws.column_dimensions["F"].width = 52

    trace_ws = workbook.create_sheet("Test Trace")
    trace_headers = [
        "Requirement ID", "Function ID", "Design Test ID", "Source Test / Implementation",
        "Test Type", "Status", "Actual Result / Evidence",
    ]
    trace_rows.sort(key=lambda row: (row[0], row[4], row[2]))
    write_case_sheet(
        trace_ws, "Detailed requirement trace", f"Test case identifiers map to source methods where available | {RUN_ID}",
        trace_headers, trace_rows,
    )
    for column, width in {
        "A": 18, "B": 16, "C": 20, "D": 66, "E": 18, "F": 18, "G": 72
    }.items():
        trace_ws.column_dimensions[column].width = width

    unit_ws = workbook.create_sheet("Unit Tests")
    unit_headers = ["Unit Test ID", "Method", "Business Requirement Link", "Status", "Actual Result"]
    unit_rows = [
        [case["Unit Test ID"], case["Phương thức"], "N/A — internal test harness",
         case["Status"], case["Actual Result"]]
        for case in cases["Unit"]
    ]
    write_case_sheet(
        unit_ws, "Unit tests — implementation-level coverage",
        "Unit tests exercise project-owned Java logic; they are not website business-flow requirements.",
        unit_headers, unit_rows,
    )
    unit_ws.column_dimensions["A"].width = 20
    unit_ws.column_dimensions["B"].width = 48
    unit_ws.column_dimensions["C"].width = 40
    unit_ws.column_dimensions["D"].width = 18
    unit_ws.column_dimensions["E"].width = 72
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)
    return path


def create_defect_workbook() -> Path:
    path = TEAM / "3. DefectReport.xlsx"
    workbook = Workbook()
    ws = workbook.active
    ws.title = "Defects"
    ws.merge_cells("A1:K1")
    ws["A1"] = "DEFECT REPORT — MOBILECITY"
    ws["A1"].font = Font(name="Arial", size=16, bold=True, color="17365D")
    ws.merge_cells("A2:K2")
    ws["A2"] = f"Baseline {RUN_ID}: không có defect được xác nhận; không tạo lỗi giả."
    ws["A2"].font = Font(name="Arial", size=10, italic=True, color="666666")
    headers = [
        "Defect ID", "Summary", "Environment", "Preconditions", "Steps to Reproduce",
        "Expected Result", "Actual Result", "Severity", "Priority", "Evidence", "Status",
    ]
    header_row = 4
    for col, header in enumerate(headers, 1):
        cell = ws.cell(header_row, col, header)
        cell.fill = PatternFill("solid", fgColor="17365D")
        cell.font = Font(name="Arial", color="FFFFFF", bold=True)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.add_table(Table(displayName="ConfirmedDefects", ref="A4:K4"))
    ws.freeze_panes = "A5"
    ws.sheet_view.showGridLines = False
    ws["A6"] = "Confirmed defect count"
    ws["B6"] = 0
    ws["A7"] = "Result note"
    ws["B7"] = "Không phát hiện lỗi tái hiện trong phạm vi đã chạy; đây không phải khẳng định website không có lỗi."
    ws["A8"] = "Unexecuted / blocked"
    ws["B8"] = "Không tạo defect từ test chưa chạy hoặc test bị BLOCKED."
    for column, width in {
        "A": 16, "B": 38, "C": 38, "D": 36, "E": 48, "F": 42,
        "G": 42, "H": 16, "I": 16, "J": 42, "K": 18,
    }.items():
        ws.column_dimensions[column].width = width
    ws.row_dimensions[4].height = 34
    workbook.save(path)
    return path


def create_markdown_converted_docs() -> list[Path]:
    outputs = [
        (
            TEAM / "1. TestPlan.docx",
            "TEST PLAN — MOBILECITY",
            "Phân tích, phạm vi, baseline và kế hoạch xác minh",
            [DOCS / "project-assessment.md", DOCS / "test-scope-and-requirements.md"],
            False,
        ),
        (
            TEAM / "6. Documentation" / "SystemAnalysis.docx",
            "PHÂN TÍCH HỆ THỐNG",
            "Mô tả hệ thống, yêu cầu nghiệp vụ và phạm vi kiểm thử",
            [DOCS / "test-scope-and-requirements.md"],
            False,
        ),
        (
            TEAM / "6. Documentation" / "UnitTestDesign.docx",
            "UNIT TEST DESIGN",
            "JUnit 5, control-flow analysis và JaCoCo",
            [DOCS / "unit-testing.md"],
            True,
        ),
        (
            TEAM / "6. Documentation" / "IntegrationTestDesign.docx",
            "INTEGRATION TEST DESIGN",
            "Các điểm tích hợp ở mức giao diện quan sát được",
            [DOCS / "integration-testing.md"],
            True,
        ),
    ]
    generated = []
    for path, title, subtitle, sources, landscape in outputs:
        create_document_from_markdown(path, title, subtitle, sources, landscape)
        generated.append(path)
    return generated


def create_report_pdf(cases: dict[str, list[dict[str, str]]]) -> Path:
    output = TEAM / "4. TestReport.pdf"
    font_dir = Path(r"C:\Windows\Fonts")
    regular_font = font_dir / "arial.ttf"
    bold_font = font_dir / "arialbd.ttf"
    if not regular_font.exists() or not bold_font.exists():
        raise FileNotFoundError("Arial Unicode fonts are required to render Vietnamese PDF text.")
    pdfmetrics.registerFont(TTFont("ArialUnicode", str(regular_font)))
    pdfmetrics.registerFont(TTFont("ArialUnicode-Bold", str(bold_font)))

    sample = getSampleStyleSheet()
    body = ParagraphStyle(
        "VietnameseBody", parent=sample["BodyText"], fontName="ArialUnicode",
        fontSize=9, leading=13, textColor=colors.HexColor("#263238"), spaceAfter=6,
    )
    heading = ParagraphStyle(
        "VietnameseHeading", parent=sample["Heading2"], fontName="ArialUnicode-Bold",
        fontSize=13, leading=17, textColor=colors.HexColor("#17365D"),
        spaceBefore=10, spaceAfter=7,
    )
    title_style = ParagraphStyle(
        "VietnameseTitle", parent=sample["Title"], fontName="ArialUnicode-Bold",
        fontSize=23, leading=28, alignment=TA_CENTER,
        textColor=colors.HexColor("#17365D"), spaceAfter=8,
    )
    caption = ParagraphStyle(
        "EvidenceCaption", parent=body, alignment=TA_CENTER, fontSize=9,
        textColor=colors.HexColor("#44546A"),
    )
    meta = ParagraphStyle("Meta", parent=body, alignment=TA_CENTER, fontSize=10)

    doc = SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm,
        topMargin=17 * mm, bottomMargin=17 * mm, title="MobileCity Test Report",
        author="IT6084 Software Testing Project",
    )
    story = [
        Spacer(1, 24 * mm),
        Paragraph("MOBILECITY", title_style),
        Paragraph("BÁO CÁO KẾT QUẢ KIỂM THỬ", title_style),
        Paragraph("Kiểm thử phần mềm — IT6084", meta),
        Paragraph(f"Baseline {RUN_ID} | 31/10/2026 | Windows / Java 17 / Chrome 156", meta),
        Spacer(1, 8 * mm),
        Paragraph("1. Tóm tắt kết quả", heading),
    ]
    summary_rows = [
        ["Chỉ số", "Kết quả thực tế"],
        ["Lệnh Maven", "mvn --batch-mode --no-transfer-progress clean verify"],
        ["JUnit test đã chạy", "33"],
        ["PASS / FAIL / BLOCKED", "32 / 0 / 1"],
        ["Maven build", "BUILD SUCCESS"],
        ["Defect được xác nhận", "0"],
        ["JaCoCo — TestConfig", "92.0% instructions; 94.6% lines; 73.1% branches"],
    ]
    story.append(make_pdf_table(summary_rows, [52 * mm, 117 * mm]))
    story.extend(
        [
            Paragraph("2. Thiết kế và trạng thái test case", heading),
        ]
    )
    category_data = [["Nhóm", "Thiết kế", "PASS", "FAIL", "BLOCKED", "NOT EXECUTED"]]
    labels = {"BlackBox": "Hộp đen", "Unit": "Unit", "Integration": "Tích hợp", "System": "Hệ thống"}
    for key in ("BlackBox", "Unit", "Integration", "System"):
        counts = case_status_counts(cases[key])
        category_data.append(
            [labels[key], str(len(cases[key])), str(counts["PASS"]), str(counts["FAIL"]),
             str(counts["BLOCKED"]), str(counts["NOT EXECUTED"])]
        )
    category_data.append(["Tổng mã case", "50", "33", "0", "1", "16"])
    story.append(make_pdf_table(category_data, [33 * mm, 22 * mm, 22 * mm, 20 * mm, 27 * mm, 45 * mm]))
    story.extend(
        [
            Spacer(1, 3 * mm),
            Paragraph(
                "Số case thiết kế được đếm theo mã định danh trong từng nhóm. Các nhóm có thể "
                "cùng dẫn chiếu tới một lần thực thi Selenium; tổng JUnit 33 là số lần test "
                "trong full suite, không phải tổng số mã thiết kế độc lập.",
                body,
            ),
            Paragraph("3. Kịch bản hệ thống đã thực thi", heading),
        ]
    )
    sys_rows = [["Test ID", "Kết quả", "Trạng thái"]]
    for case in cases["System"]:
        sys_rows.append(
            [case["Test ID"], case["Kết quả thực tế"], case["Trạng thái"]]
        )
    story.append(make_pdf_table(sys_rows, [24 * mm, 131 * mm, 24 * mm]))
    story.extend(
        [
            Paragraph("4. Coverage và defect", heading),
            Paragraph(
                "JaCoCo 0.8.12 đo riêng lớp TestConfig: 138/150 instructions (92.0%), "
                "35/37 lines (94.6%) và 19/26 branches (73.1%). Ba phương thức "
                "waitTimeout(), keepBrowserOpenSeconds() và resolveValue(...) có 100% "
                "instruction/line/branch coverage. Đây không phải coverage toàn ứng dụng "
                "Selenium hoặc website. Không có defect được xác nhận; không tạo defect "
                "từ chức năng chưa chạy hoặc case BLOCKED.",
                body,
            ),
            Paragraph("5. Giới hạn kiểm thử", heading),
            Paragraph(
                "TC-CART-001 bị BLOCKED trước đăng nhập vì thiếu credentials được ủy quyền; "
                "không thay đổi giỏ. Sắp xếp, đăng ký, tra cứu bảo hành, giao dịch thật, "
                "backend, lỗi server và timeout có kiểm soát chưa được kiểm thử. Không "
                "thực hiện thanh toán/đặt hàng hoặc CAPTCHA/OTP bypass.",
                body,
            ),
            Paragraph("6. Ảnh chụp màn hình system test", heading),
            Paragraph(
                "Các ảnh sau được Selenium tạo trong run baseline, sau khi các assertion tương ứng đạt.",
                body,
            ),
        ]
    )
    story.append(PageBreak())
    screenshot_cases = (
        ("SYS-001 — Tìm kiếm Samsung và mở trang chi tiết",
         ROOT / "screenshots" / f"{RUN_ID}-SYS-001-search-to-product-detail.png"),
        ("SYS-002 — Trạng thái không có kết quả",
         ROOT / "screenshots" / f"{RUN_ID}-SYS-002-search-empty-state.png"),
        ("SYS-003 — Trang chi tiết sau khi tải lại",
         ROOT / "screenshots" / f"{RUN_ID}-SYS-003-product-detail-after-reload.png"),
    )
    for index, (caption_text, image_path) in enumerate(screenshot_cases):
        if not image_path.is_file():
            raise FileNotFoundError(f"Missing system evidence image: {image_path}")
        image = PdfImage(str(image_path))
        max_width = A4[0] - 40 * mm
        max_height = A4[1] - 55 * mm
        scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
        image.drawWidth = image.imageWidth * scale
        image.drawHeight = image.imageHeight * scale
        story.append(Paragraph(caption_text, heading))
        story.append(image)
        story.append(Paragraph(f"Evidence file: {image_path.name}", caption))
        if index < len(screenshot_cases) - 1:
            story.append(PageBreak())

    def page_footer(canvas, document) -> None:
        canvas.saveState()
        canvas.setFont("ArialUnicode", 8)
        canvas.setFillColor(colors.HexColor("#667085"))
        canvas.drawString(18 * mm, 9 * mm, f"MobileCity QA | {RUN_ID}")
        canvas.drawRightString(A4[0] - 18 * mm, 9 * mm, f"Trang {document.page}")
        canvas.restoreState()

    output.parent.mkdir(parents=True, exist_ok=True)
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    return output


def make_pdf_table(data: list[list[str]], widths: list[float]) -> PdfTable:
    rendered = []
    for row_index, row in enumerate(data):
        rendered.append(
            [
                Paragraph(
                    html.escape(str(value)).replace("\n", "<br/>"),
                    ParagraphStyle(
                        f"cell-{row_index}-{col}",
                        fontName="ArialUnicode-Bold" if row_index == 0 else "ArialUnicode",
                        fontSize=7.6 if len(data[0]) > 4 else 8.2,
                        leading=10,
                        alignment=TA_LEFT,
                    ),
                )
                for col, value in enumerate(row)
            ]
        )
    table = PdfTable(rendered, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F4F7FB")),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7DEE8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def copy_if_present(source: Path, destination: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(f"Required evidence is missing: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def copy_evidence() -> None:
    blackbox = EVIDENCE / "BlackBox"
    unit = EVIDENCE / "UnitTest"
    integration = EVIDENCE / "Integration"
    system = EVIDENCE / "SystemTest"
    for name in (
        "TEST-mobilecity.tests.HomeTest.xml",
        "mobilecity.tests.HomeTest.txt",
        "TEST-mobilecity.tests.SearchTest.xml",
        "mobilecity.tests.SearchTest.txt",
        "TEST-mobilecity.tests.ProductTest.xml",
        "mobilecity.tests.ProductTest.txt",
    ):
        copy_if_present(ROOT / "target" / "surefire-reports" / name, blackbox / name)
    for name in (
        "TEST-mobilecity.config.TestConfigTest.xml",
        "mobilecity.config.TestConfigTest.txt",
        "TEST-mobilecity.utils.EvidenceWriterTest.xml",
        "mobilecity.utils.EvidenceWriterTest.txt",
    ):
        copy_if_present(ROOT / "target" / "surefire-reports" / name, unit / name)
    jacoco_src = ROOT / "target" / "site" / "jacoco"
    if not jacoco_src.is_dir():
        raise FileNotFoundError("JaCoCo report was not generated.")
    shutil.copytree(jacoco_src, unit / "JaCoCo", dirs_exist_ok=True)
    for name in (
        "TEST-mobilecity.tests.SearchTest.xml",
        "mobilecity.tests.SearchTest.txt",
        "TEST-mobilecity.tests.ProductTest.xml",
        "mobilecity.tests.ProductTest.txt",
    ):
        copy_if_present(ROOT / "target" / "surefire-reports" / name, integration / name)
    for name in (
        "TEST-mobilecity.tests.SystemTest.xml",
        "mobilecity.tests.SystemTest.txt",
    ):
        copy_if_present(ROOT / "target" / "surefire-reports" / name, system / name)
    for suffix in (
        "SYS-001-search-to-product-detail.png",
        "SYS-002-search-empty-state.png",
        "SYS-003-product-detail-after-reload.png",
    ):
        copy_if_present(ROOT / "screenshots" / f"{RUN_ID}-{suffix}", system / f"{RUN_ID}-{suffix}")
    copy_if_present(ROOT / "reports" / "test-execution.log", blackbox / "test-execution.log")
    copy_if_present(ROOT / "reports" / "test-execution.log", unit / "test-execution.log")
    copy_if_present(ROOT / "reports" / "test-execution.log", integration / "test-execution.log")
    copy_if_present(ROOT / "reports" / "test-execution.log", system / "test-execution.log")


def write_team_readme() -> Path:
    content = f"""# MobileCity Testing — bộ hồ sơ nộp bài

Học phần Kiểm thử phần mềm (IT6084). Baseline: `{RUN_ID}`, ngày 31/10/2026.

## Kết quả

- Lệnh chạy: `mvn --batch-mode --no-transfer-progress clean verify`
- JUnit: 33 test; 32 PASS, 0 FAIL, 0 ERROR, 1 BLOCKED.
- JaCoCo `TestConfig`: 92.0% instructions, 94.6% lines, 73.1% branches.
- Không có defect được xác nhận trong phạm vi đã chạy.
- `TC-CART-001` BLOCKED do không có credentials thử nghiệm được cấp phép; không sửa giỏ.

## Hồ sơ

- `1. TestPlan.docx`
- `2. TestCases.xlsx` — sheets Summary, BlackBox, Unit, Integration, System.
- `3. DefectReport.xlsx` — không có defect được xác nhận.
- `4. TestReport.pdf` — tổng kết, số liệu và ảnh system test.
- `6. Documentation/SystemAnalysis.docx`, `UnitTestDesign.docx`, `IntegrationTestDesign.docx`.
- `6. Documentation/TraceabilityMatrix.xlsx`.
- `8. Final/FinalReport.docx`.
- `7. Evidence/` — Surefire, JaCoCo, log và ảnh theo nhóm.

## Chạy lại

Trong thư mục phần mềm (`Team/5. Software` trong archive; hoặc repository root trong workspace):

```powershell
mvn clean test
```

Chạy nhóm riêng:

```powershell
mvn -Dtest=TestConfigTest,EvidenceWriterTest verify
mvn -Dtest=SearchTest,ProductTest test
mvn -Dtest=SystemTest test
```

`CartTest` chỉ chạy phần đăng nhập/giỏ khi có tài khoản thử nghiệm được ủy quyền qua
`MOBILECITY_USERNAME` và `MOBILECITY_PASSWORD`. Không lưu credentials trong mã,
không vượt CAPTCHA/OTP và không thực hiện thanh toán/đặt hàng.

Repository Maven gốc là ứng dụng kiểm thử; bản archive đặt bản sao mã nguồn dưới
`Team/5. Software`. Chi tiết chuyên môn và giới hạn nằm trong `docs/*.md`.
"""
    path = TEAM / "README.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return path


def validate_office_files(paths: list[Path]) -> None:
    for path in paths:
        if path.suffix == ".docx":
            with zipfile.ZipFile(path) as archive:
                if archive.testzip() is not None:
                    raise ValueError(f"Invalid DOCX archive: {path}")
                if "word/document.xml" not in archive.namelist():
                    raise ValueError(f"Missing DOCX body: {path}")
            document = Document(path)
            body_text = "\n".join(
                [paragraph.text for paragraph in document.paragraphs]
                + [cell.text for table in document.tables for row in table.rows for cell in row.cells]
            )
            if "MOBILECITY" not in body_text or len(document.tables) == 0:
                raise ValueError(f"DOCX content or tables are missing: {path}")
        elif path.suffix == ".xlsx":
            workbook = load_workbook(path, read_only=False, data_only=False)
            if not workbook.sheetnames:
                raise ValueError(f"Empty XLSX workbook: {path}")
            if path.name == "TestCases.xlsx":
                expected_sheets = {"Summary", "BlackBox", "Unit", "Integration", "System"}
                if not expected_sheets.issubset(set(workbook.sheetnames)):
                    raise ValueError(f"Test case workbook sheets are incomplete: {workbook.sheetnames}")
                for sheet_name in ("BlackBox", "Unit", "Integration", "System"):
                    ws = workbook[sheet_name]
                    status_header = next(
                        (cell.column for cell in ws[4] if cell.value in ("Status", "Trạng thái")),
                        None,
                    )
                    if status_header is None:
                        raise ValueError(f"Status column missing in {sheet_name}")
                    for row in range(5, ws.max_row + 1):
                        value = ws.cell(row, status_header).value
                        if value not in ALLOWED_STATUSES:
                            raise ValueError(f"Invalid status in {sheet_name} row {row}: {value!r}")
            if path.name == "TraceabilityMatrix.xlsx" and "Requirements" not in workbook.sheetnames:
                raise ValueError("Traceability workbook lacks Requirements sheet.")
            workbook.close()
        elif path.suffix == ".pdf":
            with path.open("rb") as pdf:
                if pdf.read(5) != b"%PDF-":
                    raise ValueError(f"Invalid PDF header: {path}")
                pdf.seek(-1024, 2)
                if b"%%EOF" not in pdf.read():
                    raise ValueError(f"PDF footer marker is missing: {path}")
            reader = PdfReader(str(path))
            if len(reader.pages) < 4:
                raise ValueError(f"Expected summary and screenshot pages in PDF: {path}")
            extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
            if "MOBILECITY" not in extracted or "SYS-001" not in extracted:
                raise ValueError(f"PDF text/evidence captions are missing: {path}")


def add_project_to_zip(archive: zipfile.ZipFile) -> None:
    package_root = "MobileCity-Testing/Team/5. Software"
    files = [
        ROOT / "README.md", ROOT / "pom.xml", ROOT / ".gitignore",
        ROOT / ".editorconfig", ROOT / ".env.example",
    ]
    directories = ("src", "docs", "scripts", ".github", ".mvn")
    for path in files:
        if path.is_file():
            archive.write(path, f"{package_root}/{path.name}")
    for dirname in directories:
        folder = ROOT / dirname
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if path.is_file() and ".git" not in path.parts and "target" not in path.parts:
                relative = path.relative_to(ROOT).as_posix()
                archive.write(path, f"{package_root}/{relative}")
    for dirname in ("surefire-reports", "site/jacoco"):
        folder = ROOT / "target" / dirname
        if folder.is_dir():
            for path in folder.rglob("*"):
                if path.is_file() and not path.name.endswith(".dumpstream"):
                    relative = path.relative_to(ROOT).as_posix()
                    archive.write(path, f"{package_root}/{relative}")
    for relative in (
        Path("reports/test-execution.log"),
    ):
        path = ROOT / relative
        if path.is_file():
            archive.write(path, f"{package_root}/{relative.as_posix()}")
    for path in (ROOT / "screenshots").glob(f"{RUN_ID}-*.png"):
        archive.write(path, f"{package_root}/screenshots/{path.name}")


def create_submission_archive() -> Path:
    archive_path = ROOT.parent / "MobileCity-Testing-submission.zip"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=8) as archive:
        readme = TEAM / "README.md"
        archive.write(readme, "MobileCity-Testing/README.md")
        for path in TEAM.rglob("*"):
            if path.is_file():
                relative = path.relative_to(TEAM).as_posix()
                archive.write(path, f"MobileCity-Testing/Team/{relative}")
        add_project_to_zip(archive)
    with zipfile.ZipFile(archive_path) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise ValueError(f"Corrupt zip member: {bad_member}")
        names = archive.namelist()
        required = (
            "MobileCity-Testing/Team/1. TestPlan.docx",
            "MobileCity-Testing/Team/2. TestCases.xlsx",
            "MobileCity-Testing/Team/3. DefectReport.xlsx",
            "MobileCity-Testing/Team/4. TestReport.pdf",
            "MobileCity-Testing/Team/6. Documentation/TraceabilityMatrix.xlsx",
            "MobileCity-Testing/Team/8. Final/FinalReport.docx",
            "MobileCity-Testing/Team/5. Software/pom.xml",
            "MobileCity-Testing/Team/5. Software/src/test/java/mobilecity/tests/SystemTest.java",
        )
        missing = [member for member in required if member not in names]
        if missing:
            raise ValueError(f"Submission archive missing required files: {missing}")
    return archive_path


def main() -> None:
    cases = load_cases()
    expected_counts = {"BlackBox": 21, "Unit": 18, "Integration": 7, "System": 4}
    for category, expected in expected_counts.items():
        if len(cases[category]) != expected:
            raise ValueError(f"{category} count changed: expected {expected}, found {len(cases[category])}")
    copy_evidence()
    write_team_readme()
    generated = create_markdown_converted_docs()
    generated.append(add_summary_docx(TEAM / "8. Final" / "FinalReport.docx", cases) or TEAM / "8. Final" / "FinalReport.docx")
    generated.extend(
        [
            create_test_cases_workbook(cases),
            create_traceability_workbook(cases),
            create_defect_workbook(),
            create_report_pdf(cases),
        ]
    )
    validate_office_files(generated)
    archive = create_submission_archive()
    for path in generated:
        print(f"Generated and validated: {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")
    print(f"Generated and validated archive: {archive} ({archive.stat().st_size} bytes)")
    print("Design case counts: " + ", ".join(f"{key}={len(value)}" for key, value in cases.items()))
    print("Overall status counts: PASS=33, FAIL=0, BLOCKED=1, NOT EXECUTED=16")


if __name__ == "__main__":
    main()
