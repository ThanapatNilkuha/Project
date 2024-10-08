import struct
import time

# โครงสร้างข้อมูลภัยพิบัติ
record_format = 'i20s20sifii20s'  # i = จำนวนเต็ม, 20s = สตริงขนาด 20 ไบต์, f = จำนวนทศนิยม
record_size = struct.calcsize(record_format)

# ฟังก์ชันแปลงสตริงให้มีขนาด 20 ไบต์
def format_string(value, size=20):
    return value.encode('utf-8').ljust(size, b'\x00')

# ฟังก์ชันเพิ่มข้อมูลใหม่
def add_record(file_name, disaster_id, disaster_type, disaster_location, 
               num_volunteers, severity_measure, num_injured, num_deaths, timestamp):
    records = []
    
    # อ่านข้อมูลเก่าทั้งหมด
    try:
        with open(file_name, 'rb') as f:
            while record := f.read(record_size):
                if len(record) == record_size:
                    unpacked_data = struct.unpack(record_format, record)
                    records.append(unpacked_data)
    except FileNotFoundError:
        # ถ้าไฟล์ไม่พบ จะสร้างไฟล์ใหม่เมื่อเพิ่มข้อมูล
        pass

    # ตรวจสอบว่ามี ID นี้อยู่แล้วหรือไม่
    for record in records:
        if record[0] == disaster_id:
            print("ID นี้มีอยู่แล้ว กรุณาเลือก ID ใหม่")
            return

    # ถ้าเป็น ID ใหม่ ให้เพิ่มข้อมูล
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
    records.append(struct.unpack(record_format, packed_data))  # เพิ่มข้อมูลที่แพ็คแล้วลงใน records

    # บันทึกข้อมูลใหม่ลงในไฟล์
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
                record[7]
            )
            f.write(packed_data)
    print("เพิ่มข้อมูลสำเร็จ")

def display_records_by_disaster_type(file_name):
    disaster_types = ["พายุ", "น้ำท่วม", "ภัยแล้ง", "ดินถล่ม"]
    print("เลือกประเภทภัยพิบัติที่ต้องการแสดง:")
    for i, dtype in enumerate(disaster_types, start=1):
        print(f"{i}. {dtype}")

    choice = int(input("กรุณาเลือกประเภท (1-4): "))
    selected_disaster_type = disaster_types[choice - 1]

    try:
        with open(file_name, 'rb') as f:
            print(f"\nแสดงข้อมูลสำหรับภัยพิบัติ: {selected_disaster_type}")
            while (record := f.read(record_size)):
                if len(record) != record_size:
                    print("ข้อมูลในไฟล์มีขนาดไม่ถูกต้อง")
                    continue  # ข้ามบันทึกที่มีขนาดไม่ถูกต้อง

                unpacked_data = struct.unpack(record_format, record)
                disaster_type = unpacked_data[1].decode('utf-8').strip()

                if disaster_type == selected_disaster_type:
                    disaster_location = unpacked_data[2].decode('utf-8').strip()
                    timestamp = unpacked_data[7].decode('utf-8').strip()
                    print(f"ID: {unpacked_data[0]}\n"
                          f"ประเภท: {disaster_type}\n"
                          f"สถานที่: {disaster_location}\n"
                          f"อาสาสมัคร: {unpacked_data[3]}\n"
                          f"ความรุนแรง: {unpacked_data[4]:.2f}\n"
                          f"บาดเจ็บ: {unpacked_data[5]}\n"
                          f"เสียชีวิต: {unpacked_data[6]}\n"
                          f"วันที่: {timestamp}\n")
    except FileNotFoundError:
        print("ไม่พบไฟล์ข้อมูล")
    except struct.error as e:
        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")



# ฟังก์ชันค้นหาข้อมูลตาม ID
def search_record_by_id(file_name, disaster_id):
    try:
        with open(file_name, 'rb') as f:
            while record := f.read(record_size):
                unpacked_data = struct.unpack(record_format, record)
                if unpacked_data[0] == disaster_id:
                    return unpacked_data
    except FileNotFoundError:
        print("ไม่พบไฟล์")
    
    print("ไม่พบข้อมูล")
    return None

# ฟังก์ชันอัปเดตข้อมูล
def update_record(file_name, disaster_id):
    records = []
    updated = False
    
    try:
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
                        record[7]
                    )
                    f.write(packed_data)
            print("อัปเดตข้อมูลสำเร็จ")
        else:
            print("ไม่พบข้อมูลสำหรับการอัปเดต")
    except FileNotFoundError:
        print("ไม่พบไฟล์")

# ฟังก์ชันลบข้อมูลตาม ID
def delete_record(file_name, disaster_id):
    records = []
    deleted = False
    
    try:
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
    except FileNotFoundError:
        print("ไม่พบไฟล์")

def main():
    file_name = "disaster_data.bin"

    while True:
        print("\nเมนู:")
        print("1. เพิ่มข้อมูล")
        print("2. แสดงข้อมูลตามประเภทภัย")
        print("3. อัปเดตข้อมูล")
        print("4. ลบข้อมูล")
        print("5. ออกจากโปรแกรม")
        
        choice = input("เลือกเมนู (1-5): ")
        
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
            timestamp = input("กรุณาใส่วันที่ (วัน/เดือน/ปี): ")
            add_record(file_name, disaster_id, disaster_type, disaster_location, 
                       num_volunteers, severity_measure, num_injured, 0, timestamp)

        # แสดงข้อมูลตามประเภทภัยพิบัติที่เลือก
        elif choice == '2':
            display_records_by_disaster_type(file_name)


        elif choice == '3':
            disaster_id = int(input("กรุณาใส่ ID ที่ต้องการอัปเดต: "))
            update_record(file_name, disaster_id)

        elif choice == '4':
            disaster_id = int(input("กรุณาใส่ ID ที่ต้องการลบ: "))
            delete_record(file_name, disaster_id)

        elif choice == '5':
            print("ออกจากโปรแกรม")
            break

        else:
            print("กรุณาเลือกเมนูที่ถูกต้อง")

if __name__ == "__main__":
    main()
