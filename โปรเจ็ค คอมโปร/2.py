import struct
import time
import datetime

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
    
    try:
        with open(file_name, 'rb') as f:
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) == record_size:
                    try:
                        unpacked_data = struct.unpack(record_format, record)
                        records.append(unpacked_data)
                    except struct.error as e:
                        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
                        continue  # ข้ามบันทึกที่ไม่สามารถถอดรหัสได้
    except FileNotFoundError:
        pass  # ถ้าไฟล์ไม่พบ จะสร้างไฟล์ใหม่เมื่อเพิ่มข้อมูล

    for record in records:
        if record[0] == disaster_id:
            print("ID นี้มีอยู่แล้ว กรุณาเลือก ID ใหม่")
            return

    new_record = (
        disaster_id,
        format_string(disaster_type),
        format_string(disaster_location),
        num_volunteers,
        severity_measure,
        num_injured,
        num_deaths,
        format_string(timestamp)
    )
    records.append(new_record)

    try:
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
    except struct.error as e:
        print(f"ข้อผิดพลาดในการบันทึกข้อมูล: {e}")

# ฟังก์ชันแสดงข้อมูลตามประเภทภัยพิบัติที่เลือก
def display_records_by_disaster_type(file_name):
    disaster_types = ["พายุ", "น้ำท่วม", "ภัยแล้ง", "ดินถล่ม"]
    print("เลือกประเภทภัยพิบัติที่ต้องการแสดง:")
    for i, dtype in enumerate(disaster_types, start=1):
        print(f"{i}. {dtype}")

    try:
        choice = int(input("กรุณาเลือกประเภท (1-4): "))
        if choice < 1 or choice > len(disaster_types):
            print("ประเภทที่เลือกไม่ถูกต้อง")
            return
    except ValueError:
        print("กรุณาใส่ตัวเลขที่ถูกต้อง")
        return

    selected_disaster_type = disaster_types[choice - 1]

    try:
        with open(file_name, 'rb') as f:
            print(f"\nแสดงข้อมูลสำหรับภัยพิบัติ: {selected_disaster_type}")
            
            # พิมพ์ส่วนหัวตาราง
            header = f"{'ID':<5} {'ประเภท':<10} {'สถานที่':<20} {'อาสาสมัคร':<12} {'ความรุนแรง':<15} {'บาดเจ็บ':<10} {'เสียชีวิต':<10} {'วันที่':<12}"
            print(header)
            print("-" * len(header))
            
            found = False  # ตัวแปรสำหรับเช็คว่ามีข้อมูลหรือไม่
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) != record_size:
                    print("ข้อมูลในไฟล์มีขนาดไม่ถูกต้อง")
                    continue  # ข้ามบันทึกที่มีขนาดไม่ถูกต้อง

                try:
                    unpacked_data = struct.unpack(record_format, record)
                except struct.error as e:
                    print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
                    continue  # ข้ามบันทึกที่ไม่สามารถถอดรหัสได้

                try:
                    disaster_type = unpacked_data[1].decode('utf-8', errors='replace').strip().replace('\x00', '')
                except UnicodeDecodeError:
                    disaster_type = "Unknown"

                # เปรียบเทียบประเภทภัยพิบัติ
                if disaster_type == selected_disaster_type:
                    disaster_id = unpacked_data[0]
                    disaster_location = unpacked_data[2].decode('utf-8', errors='replace').strip().replace('\x00', '')
                    num_volunteers = unpacked_data[3]
                    severity_measure = unpacked_data[4]
                    num_injured = unpacked_data[5]
                    num_deaths = unpacked_data[6]
                    timestamp = unpacked_data[7].decode('utf-8', errors='replace').strip().replace('\x00', '')
                    
                    # พิมพ์ข้อมูลในรูปแบบตารางแนวนอน
                    print(f"{disaster_id:<5} {disaster_type:<10} {disaster_location:<20} {num_volunteers:<12} {severity_measure:<15.2f} {num_injured:<10} {num_deaths:<10} {timestamp:<12}")
                    found = True  # ถ้าพบข้อมูลให้ปรับตัวแปรนี้

            if not found:
                print("ไม่พบข้อมูลสำหรับประเภทภัยพิบัติที่เลือก")
    except FileNotFoundError:
        print("ไม่พบไฟล์ข้อมูล")
    except struct.error as e:
        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")

# ฟังก์ชันค้นหาข้อมูลตาม ID
def search_record_by_id(file_name, disaster_id):
    try:
        with open(file_name, 'rb') as f:
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) == record_size:
                    try:
                        unpacked_data = struct.unpack(record_format, record)
                    except struct.error as e:
                        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
                        continue  # ข้ามบันทึกที่ไม่สามารถถอดรหัสได้
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
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) != record_size:
                    print("ข้อมูลในไฟล์มีขนาดไม่ถูกต้อง")
                    continue
                try:
                    unpacked_data = struct.unpack(record_format, record)
                except struct.error as e:
                    print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
                    continue  # ข้ามบันทึกที่ไม่สามารถถอดรหัสได้
                
                if unpacked_data[0] == disaster_id:
                    print("กรอกข้อมูลใหม่:")
                    print("ประเภทภัย:")
                    print("1. พายุ")
                    print("2. น้ำท่วม")
                    print("3. ภัยแล้ง")
                    print("4. ดินถล่ม")
                    try:
                        disaster_type_choice = int(input("เลือกประเภทภัย (1-4): "))
                        disaster_types = ["พายุ", "น้ำท่วม", "ภัยแล้ง", "ดินถล่ม"]
                        if disaster_type_choice < 1 or disaster_type_choice > 4:
                            print("ประเภทภัยที่เลือกไม่ถูกต้อง")
                            records.append(unpacked_data)
                            continue
                        disaster_type = disaster_types[disaster_type_choice - 1]
                    except ValueError:
                        print("กรุณาใส่ตัวเลขที่ถูกต้องสำหรับประเภทภัย")
                        records.append(unpacked_data)
                        continue
                        
                    disaster_location = input("สถานที่: ")
                    try:
                        num_volunteers = int(input("จำนวนอาสาสมัคร: "))
                        severity_measure = float(input("ค่าวัดความรุนแรง: "))
                        num_injured = int(input("จำนวนผู้บาดเจ็บ: "))
                        num_deaths = int(input("จำนวนผู้เสียชีวิต: "))
                    except ValueError:
                        print("กรุณาใส่ข้อมูลในรูปแบบที่ถูกต้องสำหรับจำนวนและค่าวัด")
                        records.append(unpacked_data)
                        continue
                        
                    timestamp = input("กรุณาใส่วันที่ (วัน/เดือน/ปี): ")
                    
                    # ใช้วันที่ปัจจุบันถ้าไม่กรอก
                    if not timestamp:
                        timestamp = time.strftime("%d/%m/%Y")
                        
                    # สร้างข้อมูลใหม่เพื่ออัปเดต
                    new_record = (
                        disaster_id,
                        format_string(disaster_type),
                        format_string(disaster_location),
                        num_volunteers,
                        severity_measure,
                        num_injured,
                        num_deaths,
                        format_string(timestamp)
                    )
                    records.append(new_record)  # เพิ่มข้อมูลใหม่
                    updated = True
                else:
                    records.append(unpacked_data)

        if updated:
            try:
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
            except struct.error as e:
                print(f"ข้อผิดพลาดในการบันทึกข้อมูล: {e}")
        else:
            print("ไม่พบข้อมูลสำหรับการอัปเดต")
    except FileNotFoundError:
        print("ไม่พบไฟล์")
    except struct.error as e:
        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")

# ฟังก์ชันลบข้อมูลตาม ID
def delete_record(file_name, disaster_id):
    records = []
    deleted = False
    
    try:
        with open(file_name, 'rb') as f:
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) != record_size:
                    print("ข้อมูลในไฟล์มีขนาดไม่ถูกต้อง")
                    continue
                try:
                    unpacked_data = struct.unpack(record_format, record)
                except struct.error as e:
                    print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
                    continue  # ข้ามบันทึกที่ไม่สามารถถอดรหัสได้

                if unpacked_data[0] != disaster_id:
                    records.append(unpacked_data)
                else:
                    deleted = True
    
        if deleted:
            try:
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
                print("ลบข้อมูลสำเร็จ")
            except struct.error as e:
                print(f"ข้อผิดพลาดในการบันทึกข้อมูล: {e}")
        else:
            print("ไม่พบข้อมูลสำหรับการลบ")
    except FileNotFoundError:
        print("ไม่พบไฟล์")
    except struct.error as e:
        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")

# ฟังก์ชันคำนวณและเปรียบเทียบข้อมูลล่าสุดกับก่อนหน้า
def compare_latest_with_previous(file_name):
    disaster_types = ["พายุ", "น้ำท่วม", "ภัยแล้ง", "ดินถล่ม"]
    print("เลือกประเภทภัยพิบัติที่ต้องการคำนวณการเปรียบเทียบ:")
    for i, dtype in enumerate(disaster_types, start=1):
        print(f"{i}. {dtype}")

    try:
        choice = int(input("กรุณาเลือกประเภท (1-4): "))
        if choice < 1 or choice > len(disaster_types):
            print("ประเภทที่เลือกไม่ถูกต้อง")
            return
    except ValueError:
        print("กรุณาใส่ตัวเลขที่ถูกต้อง")
        return

    selected_disaster_type = disaster_types[choice - 1]

    try:
        with open(file_name, 'rb') as f:
            matching_records = []
            malformed_count = 0  # ตัวนับสำหรับบันทึกที่ไม่ถูกต้อง
            while True:
                record = f.read(record_size)
                if not record:
                    break
                if len(record) != record_size:
                    print(f"พบบันทึกที่ไม่ถูกต้อง (ขนาด: {len(record)} ไบต์)")
                    malformed_count += 1
                    continue
                try:
                    unpacked_data = struct.unpack(record_format, record)
                except struct.error as e:
                    print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")
                    malformed_count += 1
                    continue  # ข้ามบันทึกที่ไม่สามารถถอดรหัสได้

                try:
                    disaster_type = unpacked_data[1].decode('utf-8', errors='replace').strip().replace('\x00', '')
                except UnicodeDecodeError as e:
                    print(f"ข้อผิดพลาดในการถอดรหัส disaster_type: {e}")
                    malformed_count += 1
                    continue

                if disaster_type == selected_disaster_type:
                    timestamp_str = unpacked_data[7].decode('utf-8', errors='replace').strip().replace('\x00', '')
                    try:
                        timestamp = datetime.datetime.strptime(timestamp_str, "%d/%m/%Y")
                    except ValueError:
                        print(f"รูปแบบวันที่ไม่ถูกต้องสำหรับ ID {unpacked_data[0]}: {timestamp_str}")
                        malformed_count += 1
                        continue
                    matching_records.append((timestamp, unpacked_data))
    
        if malformed_count > 0:
            print(f"\nพบบันทึกที่ไม่ถูกต้องทั้งหมด: {malformed_count} รายการ")

        if len(matching_records) < 2:
            print("ต้องการอย่างน้อย 2 รายการข้อมูลสำหรับการเปรียบเทียบ")
            return

        # เรียงลำดับตามวันที่
        matching_records.sort(key=lambda x: x[0])

        # ดึงข้อมูลล่าสุดและก่อนหน้า
        latest_record = matching_records[-1][1]
        previous_record = matching_records[-2][1]

        # ดึงค่าที่ต้องการเปรียบเทียบ
        latest_injured = latest_record[5]
        latest_deaths = latest_record[6]
        latest_severity = latest_record[4]

        previous_injured = previous_record[5]
        previous_deaths = previous_record[6]
        previous_severity = previous_record[4]

        # เปรียบเทียบและกำหนดสถานะ พร้อมคำนวณความแตกต่าง
        def compare(current, previous):
            difference = current - previous
            if difference > 0:
                return "เพิ่มขึ้น", difference
            elif difference < 0:
                return "ลดลง", abs(difference)
            else:
                return "เท่าเดิม", 0

        injured_status, injured_diff = compare(latest_injured, previous_injured)
        deaths_status, deaths_diff = compare(latest_deaths, previous_deaths)
        severity_status, severity_diff = compare(latest_severity, previous_severity)

        print(f"\nการเปรียบเทียบข้อมูลล่าสุดกับข้อมูลก่อนหน้า สำหรับประเภทภัยพิบัติ: {selected_disaster_type}")
        if injured_diff != 0:
            print(f"ผู้บาดเจ็บ: {previous_injured} → {latest_injured} ({injured_status} {injured_diff})")
        else:
            print(f"ผู้บาดเจ็บ: {previous_injured} → {latest_injured} ({injured_status})")
        
        if deaths_diff != 0:
            print(f"ผู้เสียชีวิต: {previous_deaths} → {latest_deaths} ({deaths_status} {deaths_diff})")
        else:
            print(f"ผู้เสียชีวิต: {previous_deaths} → {latest_deaths} ({deaths_status})")
        
        if severity_diff != 0:
            # สำหรับความรุนแรงเป็นจำนวนทศนิยม
            print(f"ความรุนแรง: {previous_severity} → {latest_severity} ({severity_status} {severity_diff:.2f})")
        else:
            print(f"ความรุนแรง: {previous_severity} → {latest_severity} ({severity_status})\n")

    except FileNotFoundError:
        print("ไม่พบไฟล์ข้อมูล")
    except struct.error as e:
        print(f"ข้อผิดพลาดในการถอดรหัสข้อมูล: {e}")

def main():
    file_name = "disaster_data.bin"

    while True:
        print("\nเมนู:")
        print("1. เพิ่มข้อมูล")
        print("2. แสดงข้อมูลตามประเภทภัย")
        print("3. อัปเดตข้อมูล")
        print("4. ลบข้อมูล")
        print("5. คำนวณการเปรียบเทียบข้อมูลล่าสุดกับก่อนหน้า")
        print("6. ออกจากโปรแกรม")
        
        choice = input("เลือกเมนู (1-6): ")
        
        if choice == '1':
            try:
                disaster_id = int(input("กรุณาใส่ ID: "))
                print("ประเภทภัย:")
                print("1. พายุ")
                print("2. น้ำท่วม")
                print("3. ภัยแล้ง")
                print("4. ดินถล่ม")
                disaster_type_choice = int(input("เลือกประเภทภัย (1-4): "))
                disaster_types = ["พายุ", "น้ำท่วม", "ภัยแล้ง", "ดินถล่ม"]
                if disaster_type_choice < 1 or disaster_type_choice > 4:
                    print("ประเภทภัยที่เลือกไม่ถูกต้อง")
                    continue
                disaster_type = disaster_types[disaster_type_choice - 1]
                disaster_location = input("กรุณาใส่สถานที่: ")
                num_volunteers = int(input("จำนวนอาสาสมัคร: "))
                severity_measure = float(input("ค่าวัดความรุนแรง: "))
                num_injured = int(input("จำนวนผู้บาดเจ็บ: "))
                num_deaths = int(input("จำนวนผู้เสียชีวิต: "))
                timestamp = input("กรุณาใส่วันที่ (วัน/เดือน/ปี): ")
                if not timestamp:
                    timestamp = time.strftime("%d/%m/%Y")
                add_record(file_name, disaster_id, disaster_type, disaster_location, 
                           num_volunteers, severity_measure, num_injured, num_deaths, timestamp)
            except ValueError:
                print("กรุณาใส่ข้อมูลในรูปแบบที่ถูกต้อง")
        
        elif choice == '2':
            display_records_by_disaster_type(file_name)
        
        elif choice == '3':
            try:
                disaster_id = int(input("กรุณาใส่ ID ที่ต้องการอัปเดต: "))
                update_record(file_name, disaster_id)
            except ValueError:
                print("กรุณาใส่ ID ในรูปแบบตัวเลข")
        
        elif choice == '4':
            try:
                disaster_id = int(input("กรุณาใส่ ID ที่ต้องการลบ: "))
                delete_record(file_name, disaster_id)
            except ValueError:
                print("กรุณาใส่ ID ในรูปแบบตัวเลข")
        
        elif choice == '5':
            compare_latest_with_previous(file_name)
        
        elif choice == '6':
            print("ออกจากโปรแกรม")
            break
        
        else:
            print("กรุณาเลือกเมนูที่ถูกต้อง")

if __name__ == "__main__":
    main()
