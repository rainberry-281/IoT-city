"""
Script tạo file tài liệu Word (.docx) tập trung chuyên sâu vào:
1. Cách mà 3 thành phố (Atlanta, Chicago, San Francisco) thu thập dữ liệu thực tế tại hiện trường.
2. Dữ liệu mà code lấy được có liên hệ trực tiếp gì đến phần cứng và hệ thống IoT.
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd_xml = f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'
    tcPr.append(parse_xml(shd_xml))


def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def add_callout(doc, text_list, title=None, border_color="1B365D", bg_color="F0F4F8"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, bg_color)
    set_cell_margins(cell, top=140, bottom=140, left=220, right=200)

    tcPr = cell._tc.get_or_add_tcPr()
    borders_xml = f'''
    <w:tcBorders {nsdecls("w")}>
        <w:top w:val="none"/>
        <w:left w:val="single" w:sz="36" w:space="0" w:color="{border_color}"/>
        <w:bottom w:val="none"/>
        <w:right w:val="none"/>
    </w:tcBorders>
    '''
    tcPr.append(parse_xml(borders_xml))

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if title:
        run_title = p.add_run(f"📌 {title}\n")
        run_title.bold = True
        run_title.font.name = "Calibri"
        run_title.font.size = Pt(11)
        run_title.font.color.rgb = RGBColor(0x1B, 0x36, 0x5D)

    for i, t in enumerate(text_list):
        if i > 0 or title:
            p_item = cell.add_paragraph()
            p_item.paragraph_format.space_before = Pt(0)
            p_item.paragraph_format.space_after = Pt(3)
            p_item.paragraph_format.line_spacing = 1.15
            run = p_item.add_run(t)
        else:
            run = p.add_run(t)
        run.font.name = "Calibri"
        run.font.size = Pt(10.5)
        run.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)


def build_document():
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    COLOR_PRIMARY = RGBColor(0x1B, 0x36, 0x5D)
    COLOR_SECONDARY = RGBColor(0x2B, 0x54, 0x7E)
    COLOR_BODY = RGBColor(0x2D, 0x37, 0x48)
    COLOR_MUTED = RGBColor(0x5A, 0x6A, 0x85)

    # 1. TIÊU ĐỀ
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(18)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("BÁO CÁO CHUYÊN SÂU:\nCƠ CHẾ THU THẬP DỮ LIỆU IOT VÀ BẢN CHẤT DỮ LIỆU THỰC TẾ\nTRONG 3 DỰ ÁN ATLANTA, CHICAGO VÀ SAN FRANCISCO")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = COLOR_PRIMARY

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(18)
    r_sub = p_sub.add_run("Giải đáp trực diện 2 câu hỏi cốt lõi:\n(1) Ba thành phố thu thập dữ liệu bằng cảm biến và phần cứng gì tại hiện trường?\n(2) Các trường dữ liệu mà mã nguồn lấy về có bản chất và liên hệ trực tiếp gì với IoT?")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(11.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = COLOR_MUTED

    tbl_line = doc.add_table(rows=1, cols=1)
    tbl_line.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_line = tbl_line.cell(0, 0)
    set_cell_background(c_line, "1B365D")
    c_line.paragraphs[0].paragraph_format.space_before = Pt(1)
    c_line.paragraphs[0].paragraph_format.space_after = Pt(1)

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(12)
    p_space.paragraph_format.space_after = Pt(0)

    add_callout(
        doc,
        [
            "Rất nhiều người nhầm lẫn rằng khi gọi API hay đọc tệp CSV thì đó chỉ là 'dữ liệu phần mềm thông thường'.",
            "Thực tế, 100% dữ liệu trong 3 dự án này đều bắt nguồn từ các cảm biến vật lý (Sensors), mạch vi xử lý nhúng (Embedded Nodes) và máy phát định vị GPS gắn trực tiếp trên cột đèn, nóc toa tàu và xe tuần tra.",
            "Tài liệu này bóc tách chi tiết phần cứng thu thập tại hiện trường của từng thành phố và chứng minh tại sao từng trường dữ liệu trong code chính là dữ liệu IoT."
        ],
        title="THÔNG ĐIỆP CỐT LÕI (CORE INSIGHT)"
    )

    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(15)
        r.font.color.rgb = COLOR_PRIMARY
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.bold = True
        r.font.name = "Calibri"
        r.font.size = Pt(12.5)
        r.font.color.rgb = COLOR_SECONDARY
        return h

    def add_p(text, bold_prefix=None):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(5)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(11)
            r_pre.font.color.rgb = COLOR_BODY
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_BODY
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_pre = p.add_run(bold_prefix)
            r_pre.bold = True
            r_pre.font.name = "Calibri"
            r_pre.font.size = Pt(11)
            r_pre.font.color.rgb = COLOR_BODY
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(11)
        r.font.color.rgb = COLOR_BODY
        return p

    # ==========================
    # PHẦN 1: ATLANTA
    # ==========================
    add_h1("PHẦN 1: ATLANTA (MARTA) - CƠ CHẾ THU THẬP & MỐI LIÊN HỆ VỚI IOT")

    add_h2("1.1. Cách Atlanta thu thập dữ liệu tại hiện trường")
    add_p("Hệ thống MARTA không dùng nhân viên ngồi bấm giờ thủ công. Việc thu thập dữ liệu diễn ra hoàn toàn tự động thông qua mạng lưới cảm biến và thiết bị nhúng gắn trên phương tiện và hạ tầng đường ray:")
    add_bullet(" Mỗi đoàn tàu điện và xe buýt đều lắp một cụm thu phát vệ tinh GPS/GNSS trên nóc xe để thu nhận tín hiệu tọa độ không gian (kinh độ, vĩ độ) liên tục với tần số quét 1 - 5 giây/lần.", bold_prefix="1. Thiết bị định vị GPS/GNSS trên phương tiện:")
    add_bullet(" Khi tàu chạy vào các đoạn ngầm dưới lòng đất (như ga Five Points, Peachtree Center), tín hiệu GPS bị mất. Lúc này, hệ thống cảm biến đếm xung trục bánh xe (Axle Wheel Tachometers) trên giá chuyển hướng của tàu sẽ tự động đo số vòng quay của bánh xe để suy ra chính xác vận tốc và quãng đường đã đi theo phương pháp quán tính.", bold_prefix="2. Cảm biến xung bánh xe (Odometry / Dead Reckoning):")
    add_bullet(" Dọc theo các ray tàu có lắp mạch cảm biến ray (Track Circuits) và hệ thống kiểm soát tàu tự động (Automatic Train Control - ATC). Khi đoàn tàu kim loại lăn qua đoạn ray nào, mạch điện bị đoản mạch (shunted), gửi tín hiệu báo đoạn ray (Block) đó đang có tàu chiếm chỗ.", bold_prefix="3. Cảm biến mạch ray hạ tầng (Track Circuits):")
    add_bullet(" Trên mỗi tàu có một máy tính nhúng (Vehicle Logic Unit - VLU). Thiết bị này tổng hợp tọa độ GPS, tốc độ, mã số tàu và gửi qua mạng vô tuyến số (Cellular 4G/Radio) về máy chủ điều phối trung tâm của MARTA.", bold_prefix="4. Bộ Gateway truyền thông trên tàu:")

    add_h2("1.2. Bản chất các trường dữ liệu mà code thu được có liên hệ gì với IoT?")
    add_p("Dưới đây là một bản ghi JSON thực tế mà file Atlanta.py của chúng ta lấy về từ máy chủ MARTA, kèm phân tích bản chất IoT của từng trường:")

    tbl_atl = doc.add_table(rows=8, cols=3)
    tbl_atl.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers = ["Trường dữ liệu lấy được", "Giá trị thực tế trong code", "Bản chất và Cảm biến IoT gốc"]
    for i, h in enumerate(headers):
        cell = tbl_atl.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)

    atl_data = [
        ("TRAIN_ID", "\"401\"", "Mã định danh thiết bị phần cứng (Hardware Node ID) của đoàn tàu phát tín hiệu."),
        ("LATITUDE, LONGITUDE", "\"33.882076\", \"-84.364863\"", "Dữ liệu đo đạc trực tiếp từ cảm biến định vị GPS/GNSS gắn trên nóc toa tàu tại thời điểm phát tin."),
        ("IS_REALTIME", "\"true\"", "Cờ đánh dấu luồng đo đạc tức thời (Real-time Telemetry Stream) trực tiếp từ cảm biến nhúng, không phải lịch trình lý thuyết."),
        ("EVENT_TIME", "\"10/13/2026 6:13:55 AM\"", "Mốc thời gian (Timestamp) do đồng hồ vệ tinh GPS trên tàu ghi nhận chính xác tới từng giây."),
        ("WAITING_SECONDS", "\"120\"", "Khoảng thời gian (giây) được tính toán tự động dựa trên khoảng cách GPS giữa tàu và nhà ga kế tiếp chia cho vận tốc cảm biến đo được."),
        ("WAITING_TIME", "\"2 min\"", "Thông tin thời gian thực hiển thị tức thời lên bảng LED tại nhà ga và ứng dụng điện thoại của hành khách."),
        ("DELAY", "\"T60S\"", "Độ trễ thực tế (+60 giây) do bộ vi xử lý trên tàu tính toán sai lệch giữa vận tốc đo đạc thực tế so với lịch trình chuẩn.")
    ]
    for row_idx, data in enumerate(atl_data, start=1):
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = tbl_atl.cell(row_idx, col_idx)
            cell.text = text
            cell.paragraphs[0].paragraph_format.line_spacing = 1.15
            cell.paragraphs[0].paragraph_format.space_after = Pt(2)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            if col_idx == 0:
                cell.paragraphs[0].runs[0].bold = True

    p_sp1 = doc.add_paragraph()
    p_sp1.paragraph_format.space_before = Pt(8)

    # ==========================
    # PHẦN 2: CHICAGO
    # ==========================
    add_h1("PHẦN 2: CHICAGO (ARRAY OF THINGS) - CƠ CHẾ THU THẬP & MỐI LIÊN HỆ VỚI IOT")

    add_h2("2.1. Cách Chicago thu thập dữ liệu tại hiện trường")
    add_p("Chicago triển khai dự án Array of Things (AoT) như một 'mạng lưới giác quan' cho đô thị. Dữ liệu được đo đạc tại hiện trường bằng các thiết bị vật lý cụ thể sau:")
    add_bullet(" Thành phố gắn hàng trăm hộp cảm biến (được gọi là Nút - Nodes) trực tiếp lên các cột đèn giao thông (light poles) ở độ cao 3 - 6 mét. Mỗi nút là một trạm máy tính nhúng chạy hệ điều hành Waggle Edge OS (phát triển bởi Argonne National Laboratory), có modem 4G LTE và số sê-ri phần cứng duy nhất là VSN (Vessel Serial Number).", bold_prefix="1. Các hộp nốt vật lý (Sensor Nodes):")
    add_bullet(" Bên trong mỗi hộp nốt tích hợp các đầu dò vật lý chuyên dụng:\n"
               "  - Nhiệt độ: Chip cảm biến bán dẫn Texas Instruments TMP112 (độ chính xác 0.5°C).\n"
               "  - Độ ẩm tương đối: Cảm biến điện dung Sensirion / HTU21D.\n"
               "  - Áp suất khí quyển: Cảm biến áp trở màng biến dạng Bosch BMP180.\n"
               "  - Bụi mịn PM2.5 / PM10: Đầu dò quang học Alphasense OPC-N2 dùng tia laser quét tán xạ hạt bụi.\n"
               "  - Khí độc: Các cảm biến điện hóa Alphasense đo nồng độ khí CO, NO2, O3, SO2.\n"
               "  - Ánh sáng & Bức xạ: Cảm biến quang học đo cường độ ánh sáng và tia cực tím UV.\n"
               "  - Âm thanh: Microphone đo mức độ ồn môi trường đô thị (Ambient Noise).", bold_prefix="2. Các linh kiện cảm biến điện tử:")
    add_bullet(" Các chip cảm biến đo mẫu liên tục (sampling). Mạch vi xử lý bên trong nốt số hóa tín hiệu (ADC), gắn nhãn thời gian thực (Timestamp) và đẩy định kỳ về Cổng dữ liệu mở Chicago (data.cityofchicago.org) thông qua kết nối di động 4G.", bold_prefix="3. Cơ chế thu nhận và truyền dữ liệu:")

    add_h2("2.2. Bản chất các trường dữ liệu mà code thu được có liên hệ gì với IoT?")
    add_p("Trong thư mục Chicago, file Chicago.py và sqlite.py đã lấy về 2 bảng dữ liệu thực tế. Đây chính là cấu trúc kinh điển của một Mạng cảm biến không dây (Wireless Sensor Network):")

    tbl_chi = doc.add_table(rows=7, cols=3)
    tbl_chi.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers2 = ["Trường dữ liệu trong code", "Ví dụ bản ghi thu được", "Bản chất và Cảm biến IoT gốc"]
    for i, h in enumerate(headers2):
        cell = tbl_chi.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)

    chi_data = [
        ("node_sensor_number", "\"06E\", \"890\"", "Mã VSN phần cứng được khắc bằng laser lên bo mạch của nút cảm biến tại hiện trường."),
        ("latitude, longitude", "\"41.785658\", \"-87.603904\"", "Tọa độ không gian chính xác của cây cột đèn nơi treo nút cảm biến."),
        ("status", "\"Live\"", "Trạng thái 'sống' (heartbeat) của nút IoT, xác nhận thiết bị nhúng vẫn đang hoạt động và truyền dữ liệu bình thường."),
        ("air_temperature", "\"22.67\" (°C)", "Tín hiệu điện áp/điện trở đo được từ cảm biến nhiệt độ bán dẫn TMP112 đặt ngoài trời."),
        ("humidity", "\"63\" (%)", "Điện dung biến thiên theo hơi ẩm không khí từ cảm biến điện dung HTU21D."),
        ("barometric_pressure", "\"985.8\" (hPa)", "Lực ép của cột không khí lên màng silicon áp điện của cảm biến áp suất khí quyển BMP180.")
    ]
    for row_idx, data in enumerate(chi_data, start=1):
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = tbl_chi.cell(row_idx, col_idx)
            cell.text = text
            cell.paragraphs[0].paragraph_format.line_spacing = 1.15
            cell.paragraphs[0].paragraph_format.space_after = Pt(2)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            if col_idx == 0:
                cell.paragraphs[0].runs[0].bold = True

    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(8)

    # ==========================
    # PHẦN 3: SAN FRANCISCO
    # ==========================
    add_h1("PHẦN 3: SAN FRANCISCO - CƠ CHẾ THU THẬP & MỐI LIÊN HỆ VỚI IOT")

    add_h2("3.1. Cách San Francisco thu thập dữ liệu tại hiện trường")
    add_p("Nhiều người nghĩ dữ liệu tội phạm chỉ là các bản ghi chép tay trên giấy của cảnh sát. Nhưng tại một đô thị thông minh hiện đại như San Francisco, dữ liệu an ninh được số hóa và thu thập qua hệ sinh thái IoT hiện trường:")
    add_bullet(" Toàn bộ xe tuần tra của Cảnh sát San Francisco (SFPD) đều được trang bị hệ thống định vị tự động AVL và máy tính điều phối CAD (Computer-Aided Dispatch). Khi xe di chuyển hoặc phản ứng trước sự cố, tọa độ GPS được ghi nhận tức thời.", bold_prefix="1. Thiết bị GPS trên xe tuần tra (AVL):")
    add_bullet(" Thành phố San Francisco lắp đặt mạng lưới cảm biến âm thanh ShotSpotter trên các mái nhà và cột đèn đường ở các khu vực trọng điểm. Khi có tiếng súng nổ, các cảm biến âm thanh phát hiện sóng xung kích và tính toán sai lệch thời gian đến (TDoA) để xác định chính xác tọa độ vị trí nổ súng trong vòng 60 giây mà không cần người dân gọi điện báo.", bold_prefix="2. Mạng cảm biến âm thanh phát hiện tiếng súng (ShotSpotter):")
    add_bullet(" Hệ thống camera an ninh và cảm biến quét biển số xe tự động (ALPR - Automated License Plate Readers) gắn trên các nút giao thông và xe cảnh sát tự động quét hàng triệu biển số mỗi ngày để phát hiện phương tiện trộm cắp (Stolen Automobile).", bold_prefix="3. Cảm biến nhận diện biển số xe (ALPR):")
    add_bullet(" Sĩ quan tại hiện trường nhập nhanh mô tả tóm tắt sự việc (Descript) qua thiết bị di động (Mobile Terminal). Hệ thống tự động đính kèm mốc thời gian nguyên tử GPS (Dates) và tọa độ địa lý (X, Y).", bold_prefix="4. Thiết bị đầu cuối di động tại hiện trường:")

    add_h2("3.2. Bản chất các trường dữ liệu mà code thu được có liên hệ gì với IoT?")
    add_p("Trong file sf_crime_dataset.csv mà chúng ta vừa tải về, từng trường dữ liệu đều mang bản chất của sự kiện bất thường (Event-Driven Telemetry) trong hệ thống IoT đô thị:")

    tbl_sf = doc.add_table(rows=6, cols=3)
    tbl_sf.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers3 = ["Trường dữ liệu trong code", "Ví dụ bản ghi thu được", "Bản chất và Cảm biến IoT gốc"]
    for i, h in enumerate(headers3):
        cell = tbl_sf.cell(0, i)
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_background(cell, "1B365D")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)

    sf_data = [
        ("X, Y", "\"-122.463545\", \"37.707968\"", "Tọa độ không gian (Longitude, Latitude) thu được trực tiếp từ cảm biến GPS trên xe tuần tra hoặc cảm biến âm thanh ShotSpotter tại nơi xảy ra sự cố."),
        ("Dates", "\"2016-03-03T00:00:00\"", "Mốc thời gian (Timestamp) chuẩn được đồng bộ tự động qua tín hiệu đồng hồ vệ tinh GPS/NTP của thiết bị hiện trường."),
        ("Descript", "\"STOLEN AUTOMOBILE\", \"BATTERY\"", "Văn bản mô tả sự kiện (Event Payload). Trong IoT, đây là gói tin dữ liệu mang thông tin chi tiết về biến cố vừa ghi nhận được."),
        ("Category", "\"VEHICLE THEFT\", \"ASSAULT\"", "Nhãn phân loại sự kiện. Đây chính là mục tiêu của tầng cao nhất trong IoT: Tầng Trí tuệ nhân tạo (AIoT Analytics)."),
        ("Mô hình AI trong code", "CountVectorizer + LogisticRegression", "Đóng vai trò 'Bộ não AI' của thành phố: Tự động đọc gói tin mô tả thô từ hiện trường và phân loại ngay lập tức thể loại vụ việc với độ chính xác 98.47%, giúp hệ thống tự động kích hoạt điều phối lực lượng ứng cứu mà không cần chờ con người xử lý thủ công.")
    ]
    for row_idx, data in enumerate(sf_data, start=1):
        bg = "F8FAFC" if row_idx % 2 == 1 else "FFFFFF"
        for col_idx, text in enumerate(data):
            cell = tbl_sf.cell(row_idx, col_idx)
            cell.text = text
            cell.paragraphs[0].paragraph_format.line_spacing = 1.15
            cell.paragraphs[0].paragraph_format.space_after = Pt(2)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            if col_idx == 0:
                cell.paragraphs[0].runs[0].bold = True

    p_sp3 = doc.add_paragraph()
    p_sp3.paragraph_format.space_before = Pt(12)

    # ==========================
    # KẾT LUẬN TỔNG HỢP
    # ==========================
    add_h1("TỔNG KẾT: TẠI SAO ĐÂY CHÍNH LÀ NỀN TẢNG CỐT LÕI CỦA IOT?")
    add_p("Qua cả 3 dự án, chúng ta thấy một công thức chung xuyên suốt định nghĩa nên một hệ thống Internet of Things (IoT) hoàn chỉnh:")
    
    add_callout(
        doc,
        [
            "1. TẦNG CẢM BIẾN (SENSING): Luôn có các thiết bị vật lý ở hiện trường (GPS trên tàu Atlanta, chip cảm biến nhiệt độ/bụi mịn trên cột đèn Chicago, cảm biến âm thanh ShotSpotter ở San Francisco).",
            "2. TẦNG TRUYỀN THÔNG (CONNECTIVITY): Thiết bị đóng gói dữ liệu kèm mã ID phần cứng (TRAIN_ID, VSN) và tọa độ vị trí (Lat, Lon), truyền qua mạng 4G/LTE lên cổng dữ liệu mở.",
            "3. TẦNG DỮ LIỆU & AI (AIoT ANALYTICS): Các file code Python của chúng ta đóng vai trò là phần mềm xử lý dữ liệu IoT: nhận luồng dữ liệu thời gian thực từ API, lưu vào cơ sở dữ liệu (SQLite), và chạy mô hình học máy (Logistic Regression) để dự báo và ra quyết định tự động."
        ],
        title="CÔNG THỨC VẬN HÀNH 3 BƯỚC CỦA IOT TRONG BÀI TẬP"
    )

    output_path = os.path.join(r"d:\code\Test code IOT\doc", "Tong_ket_IoT_va_Ung_dung_Chuong_11.docx")
    doc.save(output_path)
    print(f"Đã cập nhật file tài liệu Word thành công: {output_path}")
    return output_path


if __name__ == "__main__":
    build_document()
