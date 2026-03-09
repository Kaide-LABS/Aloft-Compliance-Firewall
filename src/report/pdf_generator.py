from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import datetime


COLORS = {
    "GREEN": HexColor("#28a745"),
    "AMBER": HexColor("#ffc107"),
    "RED": HexColor("#dc3545"),
    "header_bg": HexColor("#1a1a2e"),
    "light_gray": HexColor("#f8f9fa"),
    "text": HexColor("#212529"),
    "muted": HexColor("#6c757d"),
}


def generate_compliance_pdf(
    result: dict, postcode: str, company_name: str, elapsed: float
) -> bytes:
    """Generate a professional PDF compliance report. Returns bytes."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        textColor=COLORS["header_bg"],
        spaceAfter=5 * mm,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=COLORS["muted"],
        spaceAfter=10 * mm,
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=COLORS["header_bg"],
        spaceBefore=8 * mm,
        spaceAfter=4 * mm,
    )
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontSize=10,
        textColor=COLORS["text"],
        spaceAfter=3 * mm,
        leading=14,
    )
    verdict_style = ParagraphStyle(
        "Verdict",
        parent=styles["Normal"],
        fontSize=16,
        alignment=TA_CENTER,
        spaceAfter=5 * mm,
    )

    elements = []

    # --- Header ---
    elements.append(Paragraph("Compliance Report", title_style))
    elements.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y at %H:%M')} | "
            f"Postcode: {postcode} | "
            f"Processing time: {elapsed:.1f}s",
            subtitle_style,
        )
    )
    elements.append(HRFlowable(width="100%", thickness=1, color=COLORS["muted"]))
    elements.append(Spacer(1, 5 * mm))

    # --- Verdict ---
    level = result.get("risk_level", "UNKNOWN")
    score = result.get("risk_score", 0)
    level_text = {
        "GREEN": "CLEAR TO LEASE",
        "AMBER": "PROCEED WITH CAUTION",
        "RED": "DO NOT LEASE",
    }.get(level, "UNKNOWN")
    verdict_color = COLORS.get(level, COLORS["muted"])

    verdict_data = [
        [
            Paragraph(
                f"<b>{level}: {level_text}</b>",
                ParagraphStyle("v", parent=verdict_style, textColor=verdict_color),
            ),
            Paragraph(
                f"<b>Risk Score: {score}/100</b>",
                ParagraphStyle("s", parent=verdict_style, textColor=verdict_color),
            ),
        ]
    ]
    verdict_table = Table(verdict_data, colWidths=[90 * mm, 80 * mm])
    verdict_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COLORS["light_gray"]),
                ("BOX", (0, 0), (-1, -1), 1, verdict_color),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(verdict_table)
    elements.append(Spacer(1, 5 * mm))

    # --- Summary ---
    elements.append(Paragraph("Executive Summary", heading_style))
    elements.append(
        Paragraph(result.get("summary", "No summary available."), body_style)
    )

    # --- EPC Data ---
    epc = result.get("epc_data", {})
    elements.append(Paragraph("Property Data — EPC Certificate", heading_style))
    if epc.get("found"):
        epc_rows = [
            ["Field", "Value"],
            ["Address", epc.get("address", "N/A")],
            ["Current Rating", epc.get("rating", "N/A")],
            ["Potential Rating", epc.get("potential_rating", "N/A")],
            ["Property Type", epc.get("property_type", "N/A")],
            ["Lodgement Date", epc.get("lodgement_date", "N/A")],
        ]
        epc_table = Table(epc_rows, colWidths=[50 * mm, 120 * mm])
        epc_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COLORS["header_bg"]),
                    ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.5, COLORS["muted"]),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [HexColor("#ffffff"), COLORS["light_gray"]],
                    ),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(epc_table)
    else:
        elements.append(
            Paragraph(
                f"No EPC certificate found: {epc.get('error', 'Unknown')}", body_style
            )
        )

    # --- Company Data ---
    company = result.get("company_data", {})
    if company_name:
        elements.append(Paragraph("Company Verification", heading_style))
        if company.get("found"):
            comp_rows = [
                ["Field", "Value"],
                ["Company Name", company.get("company_name", "N/A")],
                ["Company Number", company.get("company_number", "N/A")],
                ["Status", company.get("status", "N/A")],
                ["Type", company.get("type", "N/A")],
            ]
            comp_table = Table(comp_rows, colWidths=[50 * mm, 120 * mm])
            comp_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), COLORS["header_bg"]),
                        ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("GRID", (0, 0), (-1, -1), 0.5, COLORS["muted"]),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [HexColor("#ffffff"), COLORS["light_gray"]],
                        ),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            elements.append(comp_table)
        else:
            elements.append(
                Paragraph("Company not found in Companies House register.", body_style)
            )

    # --- Violations ---
    violations = result.get("violations", [])
    elements.append(Paragraph(f"Violations ({len(violations)})", heading_style))
    if violations:
        for v in violations:
            elements.append(
                Paragraph(
                    f"<b>[{v.get('severity', 'HIGH')}]</b> {v['description']}<br/>"
                    f"<i>Legislation: {v.get('legislation', 'N/A')}</i>",
                    body_style,
                )
            )
    else:
        elements.append(Paragraph("No compliance violations detected.", body_style))

    # --- Warnings ---
    warnings = result.get("warnings", [])
    elements.append(Paragraph(f"Warnings ({len(warnings)})", heading_style))
    if warnings:
        for w in warnings:
            text = w["description"]
            if w.get("expires_in_days"):
                text += f" (expires in {w['expires_in_days']} days)"
            elements.append(Paragraph(text, body_style))
    else:
        elements.append(Paragraph("No compliance warnings.", body_style))

    # --- Legal Requirements ---
    reqs = result.get("legal_requirements", [])
    elements.append(
        Paragraph(f"Legal Requirements Checked ({len(reqs)})", heading_style)
    )
    if reqs:
        req_rows = [["Requirement", "Legislation", "Section"]]
        for r in reqs:
            req_rows.append(
                [
                    Paragraph(
                        r.get("requirement", ""),
                        ParagraphStyle("rc", fontSize=8, leading=10),
                    ),
                    Paragraph(
                        r.get("legislation", ""),
                        ParagraphStyle("rl", fontSize=8, leading=10),
                    ),
                    r.get("section", ""),
                ]
            )
        req_table = Table(req_rows, colWidths=[80 * mm, 55 * mm, 35 * mm])
        req_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COLORS["header_bg"]),
                    ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#ffffff")),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, COLORS["muted"]),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [HexColor("#ffffff"), COLORS["light_gray"]],
                    ),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        elements.append(req_table)

    # --- Footer ---
    elements.append(Spacer(1, 10 * mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=COLORS["muted"]))
    elements.append(
        Paragraph(
            f"Report generated by Aloft Compliance Firewall | "
            f"Estimated cost: ~£0.01 | "
            f"Processing time: {elapsed:.1f}s | "
            f"This report is for informational purposes only and does not constitute legal advice.",
            ParagraphStyle(
                "footer",
                parent=body_style,
                fontSize=7,
                textColor=COLORS["muted"],
                alignment=TA_CENTER,
            ),
        )
    )

    doc.build(elements)
    return buffer.getvalue()
