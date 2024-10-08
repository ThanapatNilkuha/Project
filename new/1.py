def analyze_log_file(log_file_path: str) -> dict:
    requests_by_ip = {}
    resource_count = {}
    total_404_errors = 0
    total_bytes = 0
    
    # เปิดไฟล์และอ่านข้อมูลทีละบรรทัด
    with open(log_file_path, 'r') as file:
        for line in file:
            # แยกบรรทัดเป็นส่วน ๆ
            parts = line.split()
            
            # ตรวจสอบว่าข้อมูลในบรรทัดมีครบตามรูปแบบที่กำหนดหรือไม่
            if len(parts) != 5:
                continue  # ข้ามบรรทัดที่ข้อมูลไม่ครบ
            
            ip, method, resource, status, byte_size = parts
            
            # นับจำนวนการร้องขอจากแต่ละ IP
            if ip in requests_by_ip:
                requests_by_ip[ip] += 1
            else:
                requests_by_ip[ip] = 1
            
            # นับจำนวนการร้องขอแต่ละ resource
            if resource in resource_count:
                resource_count[resource] += 1
            else:
                resource_count[resource] = 1
            
            # นับจำนวนการร้องขอที่มีสถานะ 404
            if status == '404':
                total_404_errors += 1
            
            # รวมขนาดของการร้องขอ
            total_bytes += int(byte_size)
    
    # ตรวจสอบว่ามีทรัพยากรที่ถูกเรียกร้องหรือไม่
    if resource_count:
        most_requested_resource = max(resource_count, key=resource_count.get)
    else:
        most_requested_resource = None  # หรือ "No resources requested"
    
    # ส่งคืนผลลัพธ์ในรูปแบบ dictionary
    return {
        "requests_by_ip": requests_by_ip,
        "most_requested_resource": most_requested_resource,
        "total_404_errors": total_404_errors,
        "total_bytes": total_bytes
    }

# เรียกใช้ฟังก์ชันและแสดงผลลัพธ์
log_file_path = 'server_log.txt'  # เปลี่ยนเป็นไฟล์ log ของคุณ
result = analyze_log_file(log_file_path)

# แสดงผลลัพธ์การวิเคราะห์
print("Log File Analysis Result:")
print(f"Requests by IP: {result['requests_by_ip']}")
print(f"Most Requested Resource: {result['most_requested_resource']}")
print(f"Total 404 Errors: {result['total_404_errors']}")
print(f"Total Bytes Transferred: {result['total_bytes']}")
