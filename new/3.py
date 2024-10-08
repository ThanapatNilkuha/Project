import struct
import time
import os

# โครงสร้างข้อมูลภัยพิบัติ
record_format = 'i20s20sifii20s'  # i = จำนวนเต็ม, 20s = สตริงขนาด 20 ไบต์, f = จำนวนทศนิยม
record_size = struct.calcsize(record_format)

# ฟังก์ชันแปลงสตริงให้มีขนาด 20 ไบต์
def format_string(value, size=20):
    return value.encode('utf-8').ljust(size, b'\x00')

# ฟังก์ชันเพิ่มข้อมูลใหม่
def add_record(file_name, disaster_id, disaster_type, disaster_location, 
               num_volunteers, severity_measure, num_injured, num_deaths, timestamp):
    with open(file_name, 'ab') as f:
        packed_data = struct.pack(
            record_format,
            disaster_id,
            format_string(disaster_type),
            format_string(disaster_location),
            num_volunteers,
            severity_measure,
            num_injured,
            num_deaths,
            format_string(timestamp)
        )
        f.write(packed_data)
        print("เพิ่มข้อมูลสำเร็จ")

# ฟังก์ชันแสดงข้อมูลทั้งหมด
def display_all_records(file_name):
    if not os.path.exists(file_name):
        print("ไม่พบไฟล์ข้อมูล")
        return

    with open(file_name, 'rb') as f:
        while (record := f.read(record_size)):
            # ตรวจสอบว่าขนาดข้อมูลตรงตามที่คาดไว้
            if len(record) != record_size:
                print(f"ข้อมูลในไฟล์มีขนาดไม่ถูกต้อง: ขนาดที่อ่านได้ = {len(record)}, ค่าที่คาดไว้ = {record_size}")
                continue

            # พยายามทำการถอดรหัสข้อมูล
            unpacked_data = struct.unpack(record_format, record)
            disaster_type = unpacked_data[1].decode('utf-8').strip()
            disaster_location = unpacked_data[2].decode('utf-8').strip()
            timestamp = unpacked_data[7].decode('utf-8').strip()

            print(f"ID: {unpacked_data[0]}, "
                  f"ประเภท: {disaster_type}, "
                  f"สถานที่: {disaster_location}, "
                  f"อาสาสมัคร: {unpacked_data[3]}, "
                  f"ความรุนแรง: {unpacked_data[4]:.2f}, "
                  f"บาดเจ็บ: {unpacked_data[5]}, "
                  f"เสียชีวิต: {unpacked_data[6]}, "
                  f"วันที่: {timestamp}")

# ฟังก์ชันค้นหาข้อมูลตาม ID
def search_record_by_id(file_name, disaster_id):
    if not os.path.exists(file_name):
        print("ไม่พบไฟล์")
        return None
    
    with open(file_name, 'rb') as f:
        while record := f.read(record_size):
            unpacked_data = struct.unpack(record_format, record)
            if unpacked_data[0] == disaster_id:
                return unpacked_data
    print("ไม่พบข้อมูล")
    return None

# ฟังก์ชันอัปเดตข้อมูล
# ฟังก์ชันอัปเดตข้อมูล
def update_record(file_name, disaster_id):
    records = []
    updated = False
    
    with open(file_name, 'rb') as f:
        while record := f.read(record_size):
            unpacked_data = struct.unpack(record_format, record)
            if unpacked_data[0] == disaster_id:
                print("กรอกข้อมูลใหม่:")
                disaster_type = input("ประเภทภัย: ")
                disaster_location = input("สถานที่: ")
                num_volunteers = int(input("จำนวนอาสาสมัคร: "))
                severity_measure = float(input("ค่าวัดความรุนแรง: "))
                num_injured = int(input("จำนวนผู้บาดเจ็บ: "))
                timestamp = input("กรุณาใส่วันที่ (วัน/เดือน/ปี): ")
                
                # ใช้วันที่ปัจจุบันถ้าไม่กรอก
                if not timestamp:
                    timestamp = time.strftime("%d/%m/%Y")
                    
                # สร้างข้อมูลใหม่เพื่ออัปเดต
                new_data = (
                    disaster_id,
                    format_string(disaster_type),
                    format_string(disaster_location),
                    0,  # จำนวนองค์กร ไม่ได้ใช้งาน
                    num_volunteers,
                    severity_measure,
                    num_injured,
                    0,  # จำนวนผู้เสียชีวิต ไม่ได้ใช้งาน
                    format_string(timestamp)
                )
                records.append(new_data)  # เพิ่มข้อมูลใหม่
                updated = True
            else:
                records.append(unpacked_data)
    
    if updated:
        with open(file_name, 'wb') as f:
            for record in records:
                packed_data = struct.pack(
                    record_format,
                    record[0],
                    record[1],
                    record[2],
                    record[3],
                    record[4],
                    record[5],
                    record[6],
                    record[7],
                    record[8]
                )
                f.write(packed_data)
        print("อัปเดตข้อมูลสำเร็จ")
    else:
        print("ไม่พบข้อมูลสำหรับการอัปเดต")


# ฟังก์ชันลบข้อมูลตาม ID
def delete_record(file_name, disaster_id):
    records = []
    deleted = False
    
    if not os.path.exists(file_name):
        print("ไม่พบไฟล์")
        return
    
    with open(file_name, 'rb') as f:
        while record := f.read(record_size):
            unpacked_data = struct.unpack(record_format, record)
            if unpacked_data[0] != disaster_id:
                records.append(unpacked_data)
            else:
                deleted = True
    
    if deleted:
        with open(file_name, 'wb') as f:
            for record in records:
                packed_data = struct.pack(
                    record_format,
                    record[0],
                    format_string(record[1].decode('utf-8')) if isinstance(record[1], bytes) else record[1],
                    format_string(record[2].decode('utf-8')) if isinstance(record[2], bytes) else record[2],
                    record[3],
                    record[4],
                    record[5],
                    record[6],
                    format_string(record[7].decode('utf-8')) if isinstance(record[7], bytes) else record[7]
                )
                f.write(packed_data)
        print("ลบข้อมูลสำเร็จ")
    else:
        print("ไม่พบข้อมูลสำหรับการลบ")

# ฟังก์ชันหลักของระบบ
def main():
    file_name = "disaster_data.bin"

    # ลบไฟล์เดิมถ้ามี
    if os.path.exists(file_name):
        os.remove(file_name)

    while True:
        print("\nเมนู:")
        print("1. เพิ่มข้อมูล")
        print("2. แสดงข้อมูลทั้งหมด")
        print("3. ค้นหาข้อมูลตาม ID")
        print("4. อัปเดตข้อมูล")
        print("5. ลบข้อมูล")
        print("6. ออกจากโปรแกรม")
        
        choice = input("เลือกเมนู (1-6): ")
        
        if choice == '1':
            disaster_id = int(input("กรุณาใส่ ID: "))
            print("ประเภทภัย:")
            print("1. พายุ")
            print("2. น้ำท่วม")
            print("3. ภัยแล้ง")
            print("4. ดินถล่ม")
            disaster_type_choice = int(input("เลือกประเภทภัย (1-4): "))
            disaster_types = ["พายุ", "น้ำท่วม", "ภัยแล้ง", "ดินถล่ม"]
            disaster_type = disaster_types[disaster_type_choice - 1]
            disaster_location = input("กรุณาใส่สถานที่: ")
            num_volunteers = int(input("จำนวนอาสาสมัคร: "))
            severity_measure = float(input("ค่าวัดความรุนแรง: "))
            num_injured = int(input("จำนวนผู้บาดเจ็บ: "))
            num_deaths = int(input("จำนวนผู้เสียชีวิต: "))
            timestamp = input("กรุณาใส่วันที่ (รูปแบบ: วัน/เดือน/ปี) หรือกด Enter เพื่อใช้วันที่ปัจจุบัน: ")
            if not timestamp:
                timestamp = time.strftime("%d/%m/%Y")  # ใช้วันที่ปัจจุบันถ้าไม่กรอก
            add_record(file_name, disaster_id, disaster_type, disaster_location, 
                       num_volunteers, severity_measure, num_injured, num_deaths, timestamp)
        elif choice == '2':
            display_all_records(file_name)  # แสดงข้อมูลทั้งหมด
        elif choice == '3':
            disaster_id = int(input("กรุณาใส่ ID ที่ต้องการค้นหา: "))
            record = search_record_by_id(file_name, disaster_id)
            if record:
                print(f"ID: {record[0]}, "
                      f"ประเภท: {record[1].decode('utf-8').strip()}, "
                      f"สถานที่: {record[2].decode('utf-8').strip()}, "
                      f"อาสาสมัคร: {record[3]}, "
                      f"ความรุนแรง: {record[4]:.2f}, "
                      f"บาดเจ็บ: {record[5]}, "
                      f"เสียชีวิต: {record[6]}, "
                      f"วันที่: {record[7].decode('utf-8').strip()}")
        elif choice == '4':
            disaster_id = int(input("กรุณาใส่ ID ที่ต้องการอัปเดต: "))
            update_record(file_name, disaster_id)
        elif choice == '5':
            disaster_id = int(input("กรุณาใส่ ID ที่ต้องการลบ: "))
            delete_record(file_name, disaster_id)
        elif choice == '6':
            print("ออกจากโปรแกรม")
            break
        else:
            print("เลือกไม่ถูกต้อง กรุณาเลือกใหม่")

if __name__ == "__main__":
    main()
