import pyinputplus as pypi
import copy
from datetime import datetime
import mysql.connector
import sys

koneksi = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="capstone_1"
)

dataStorage = {"header":("ID","Capacity")}
dataSupplier = {"header": ("ID","Nama","Alamat","Kontak")}
dataBarang = {"header": ("ID", "Nama", "Tgl Beli", "Harga Beli","Expired Date", "Quantity Barang", "Lokasi", "Supplier")}
dataPengeluaran= { "header": ("ID","Id Barang","Kategori","Jml Keluar","Tgl keluar")}
dataStatusExpired = {"header":("Id Barang","Nama Barang","Expired Date","Status")}

kursor = koneksi.cursor()

def fetchData():
    kueri = ["SELECT * FROM storage",
            "SELECT * FROM supplier",
            "SELECT b.*, s.nama FROM barang b JOIN supplier s on s.id = b.supplier",
            "SELECT * FROM pengeluaran"]
    
    for query in kueri:
        kursor.execute(query)
        rows = kursor.fetchall()

        for row in rows:
            row = list(row)
            if row[0][:4] == "brg-":
                row[2], row[4] = row[2].strftime("%Y/%m/%d"), row[4].strftime("%Y/%m/%d")
                row.pop(-2)
                dataBarang[row[0]] = row

            elif row[0][:5] == "supp-": dataSupplier[row[0]] = row
            elif row[0][:4] == "lok-": dataStorage[row[0]] = row
            elif row[0][:4] == "out-": 
                row[-1] = row[-1].strftime("%Y/%m/%d")
                dataPengeluaran[row[0]] = row
            row.pop(0)

def printFormatList(data):
    cloneData = copy.deepcopy(data)
    
    for keys, values in cloneData.items():
        if keys != "header":
            values.insert(0,keys)

    for key, value in cloneData.items():
        if key != "header":
            print("\n".join([f"{cloneData['header'][i]}: {v}" for i, v in enumerate(value)]))
        print()

def printFormatTable(data):
    cloneData = copy.deepcopy(data)

    for keys, values in cloneData.items():
        if keys != "header":
            values.insert(0, keys)

    #Calculation
    maxWidths = [max(len(str(row[i])) for row in cloneData.values()) for i in range(len(cloneData["header"]))]
    format_string = ' | '.join(['{{:<{}}}'.format(width) for width in maxWidths])
    line_length = sum(maxWidths) + 3 * (len(maxWidths) - 1)

    #Print the formats
    print('-' * line_length)
    print(format_string.format(*cloneData["header"]))
    print('-' * line_length)
    for keys, values in cloneData.items():
        if keys != "header":
            print(format_string.format(*values))
    print('-' * line_length)


def availableStorage(amountQty=0):
    cloneData = copy.deepcopy(dataStorage)
    for key, value in dataBarang.items():
        if key != "header":
            quantity = value[-3]
            lokasi = value[-2]
            if lokasi in cloneData.keys():
                cloneData[lokasi][0] -= quantity
    availableStorage = {key : value for key, value in cloneData.items() if key != "header" and amountQty <= value[0] or key == "header"}

    return availableStorage

def sortingExpired():
    date_list = []
    for key, value in dataBarang.items():
        if key != "header":
            date_list.append([key,value[0],value[-4]])

    n = len(date_list)

    for i in range(n - 1):
        for j in range(0, n - i - 1): 
            if date_list[j][2] > date_list[j + 1][2]:
                date_list[j], date_list[j + 1] = date_list[j + 1], date_list[j]

    def calculateExpiredDay(date):
        today = datetime.today().date()
        date = datetime.strptime(date, "%Y/%m/%d").date()
        difference = date - today
        if difference.days < 1:
            return "| EXPIRED |"

        selisihHari = difference.days
        tahun = selisihHari // 360
        selisihHari = selisihHari % 360

        bulan = selisihHari // 30
        selisihHari = selisihHari % 30

        minggu = selisihHari // 7
        selisihHari = selisihHari % 7
        result =''
        if tahun:
            result += f"{tahun} thn "
        if bulan:
            result += f"{bulan} bln "
        if minggu:
            result += f"{minggu} minggu "
        if selisihHari:
            result += f"{selisihHari} hari"

        return result
    
    for i,date in enumerate(date_list):
        date.append(calculateExpiredDay(date[-1]))
        dataStatusExpired[date[0]] = date[1:]

def read():
    print("""
    Pilih menu:
        1. Tampil Semua Data Barang
        2. Cari Barang Berdasarkan id
        3. Tampil Data Supplier
        4. Tampil Data Kapasitas Storage
        5. Tampil Data Pengeluaran Barang
        6. Tampil Status Expired Barang
        7. Back to Menu
    """)

    def findBarang():
        inputId = str(input("Input id barang untuk dicari: "))
        printFormatList({"header": dataBarang["header"] ,inputId : dataBarang[inputId]})
    
    inputMenuRead = pypi.inputInt(prompt='Pilih menu (1-7): ', lessThan=8)
    
    if inputMenuRead == 1: printFormatTable(dataBarang)
    elif inputMenuRead == 2: findBarang()
    elif inputMenuRead == 3: printFormatTable(dataSupplier)
    elif inputMenuRead == 4: printFormatTable(availableStorage())
    elif inputMenuRead == 5: printFormatTable(dataPengeluaran)
    elif inputMenuRead == 6: 
        sortingExpired()
        printFormatTable(dataStatusExpired)
    else: main()
    read()

def add():
    print("""
    Pilih menu:
        1. Tambah Barang
        2. Tambah Supplier
        3. Back to Menu
    """)

    def add_barang():
        inputId = str(input("Buat id barang: "))

        if inputId in dataBarang.keys():
            print("Data already exist")
            add()
        else:     
            inputNama = str(input("Input nama barang: "))
            inputTglBeli = pypi.inputDate(prompt='Input tgl beli: ').strftime("%Y/%m/%d")
            inputHarga = pypi.inputInt(prompt='Input harga barang: ')
            inputExpired = pypi.inputDate(prompt='Input tgl expired barang: ').strftime("%Y/%m/%d")
            printFormatTable(availableStorage())
            inputQuantity = pypi.inputInt(prompt='Input quantity barang: ')

            #filtering storage yg kapasitas memenuhi dari qty
            validStorage =  [keys for keys in availableStorage(inputQuantity).keys() if keys != "header"]
            if len(validStorage) < 1:
                print("Semua kapasitas penyimpanan tidak cukup utk brg ini!")
                add()
            
            printFormatTable(availableStorage(inputQuantity))
            inputLokasi =  pypi.inputChoice(prompt="Pilih id lokasi barang: ",choices= validStorage,blank=True)
            printFormatTable(dataSupplier)
            inputSupplier = str(input("Pilih supplier by ID: "))

            if inputSupplier not in dataSupplier.keys():
                inputCondSupp =str(input('Data supplier tidak ditemukan apakah ingin menambahkan data supplier?(y/n) ')).lower()
                if inputCondSupp == "y": 
                    inputSupplier = add_supplier("add_barang")
                else:
                    add()
            inputSave =str(input('Apakah data barang ingin disimpan?(y/n) '))
            if inputSave =="y":
                values = [inputId,inputNama,inputTglBeli,inputHarga,inputExpired,inputQuantity,inputLokasi,inputSupplier]
                #Store to dict
                dataBarang[inputId] = values[1:]

                #Store to db
                sql = "INSERT INTO barang VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
                kursor.execute(sql, values)
                koneksi.commit()
                print("Data is successfully saved!")
                add()
            else:
                add()

    def add_supplier(callingFrom=""):
        inputId = str(input("Buat id supplier: "))

        if inputId in dataSupplier.keys():
            print("Data already exist")
            add()
        else:
            inputNama = str(input("Input nama supplier: "))
            inputAlamat = str(input("Input alamat supplier: "))
            inputKontak = str(input("Input kontak supplier: "))
            inputSave =str(input('Apakah data supplier ingin disimpan?(y/n) '))

            if inputSave == "y":
                values = [inputId,inputNama, inputAlamat, inputKontak]
                dataSupplier[inputId] = values[1:]
                sql = "INSERT INTO supplier VALUES(%s,%s,%s,%s)"
                kursor.execute(sql, values)
                koneksi.commit()
                print("Data is successfully saved!")
                
                if callingFrom != "add_barang": add()
                return inputId
            else: add()

    inputMenuTambah = pypi.inputInt(prompt='Pilih menu (1-3): ', lessThan=4)
    if inputMenuTambah == 1: add_barang()
    elif inputMenuTambah == 2: add_supplier()
    elif  inputMenuTambah == 3: main()

def update():
    print("""
    Pilih menu:
        1. Update Barang
        2. Update Supplier
        3. Back to Menu
    """)
    inputMenuUbah = pypi.inputInt(prompt='Pilih menu (1-2): ', lessThan=4)
    
    def update_barang():
        printFormatTable(dataBarang)
        inputId = pypi.inputStr(prompt="Input id barang yg ingin diubah: ",blockRegexes=["header","HEADER"])

        if inputId not in dataBarang.keys():
            print("The data you are looking for does not exist!")
            update()
        else:
            print("Data would update according the ID")
            printDict= {"header": dataBarang["header"] ,inputId : dataBarang[inputId]}
            printFormatList(printDict)
            inputConfirm = str(input('Continue update?(y/n) '))
            if inputConfirm == "y":
                inputNama = str(input("Ubah nama barang: "))
                inputTglBeli = pypi.inputDate(prompt='Ubah tgl beli: ').strftime("%Y/%m/%d")
                inputHarga = pypi.inputInt(prompt='Ubah harga barang: ')
                inputExpired = pypi.inputDate(prompt='Ubah tgl expired barang: ').strftime("%Y/%m/%d")
                inputQuantity = pypi.inputInt(prompt='Ubah quantity barang: ')
                printFormatTable(availableStorage(inputQuantity))
                inputLokasi = pypi.inputChoice(prompt="Pilih lokasi barang: ", choices= list(availableStorage(inputQuantity).keys()))
                printFormatTable(dataSupplier)
                inputSupplier = pypi.inputChoice(prompt="Pilih supplier by ID: ", choices= [keys for keys in dataSupplier.keys() if keys != "header"])
                
                values = [inputNama,inputTglBeli,inputHarga,inputExpired,inputQuantity,inputLokasi,inputSupplier,inputId]
                dataBarang[inputId] = values[:-2]
                
                sql = "UPDATE barang SET nama=%s, tgl_beli=%s, harga_beli=%s, date_expired=%s, quantity_barang=%s, lokasi=%s, supplier=%s WHERE id=%s"
                kursor.execute(sql, values)
                koneksi.commit()
                print("Data is successfully updated!")
                update()
            else:
                update()
    
    def update_supplier():
        printFormatTable(dataSupplier)
        inputId = pypi.inputStr(prompt="Input id supplier yg ingin diubah: ",blockRegexes=["header","HEADER"])

        if inputId not in dataSupplier.keys():
            print("The data you are looking for does not exist!")
            update()
        else:
            inputNama = str(input("Input nama supplier: "))
            inputAlamat = str(input("Input alamat supplier: "))
            inputKontak = str(input("Input kontak supplier: "))

            inputConfirm = str(input('Continue update?(y/n) '))
            if inputConfirm == "y":
                values = [ inputNama, inputAlamat, inputKontak,inputId]
                dataSupplier[inputId] = values[:-2]

                sql = "UPDATE supplier SET nama=%s, alamat=%s, kontak=%s WHERE id=%s"
                kursor.execute(sql, values)
                koneksi.commit()
                print("Data is successfully updated!")
                update()
            else: update()

    if inputMenuUbah == 1: update_barang()
    elif inputMenuUbah == 2: update_supplier()
    elif  inputMenuUbah == 3: main()

def delete():
    print("""
    Pilih menu:
        1. Delete/Pengeluaran Barang
        2. Delete Supplier
        3. Back to Menu
    """)

    def delete_barang():

        printFormatTable(dataBarang)
        inputId = pypi.inputStr(prompt="Pilih id barang yg ingin dihapus/dikeluarkan: ",blockRegexes=["header","HEADER"])

        if inputId not in dataBarang.keys():
            print("The data you are looking for does not exist!")
        else:
            printDict= {"header": dataBarang["header"] ,inputId : dataBarang[inputId]}
            printFormatList(printDict)
            print("""
            Pilih menu index:
                1. Penghapusan Barang
                2. Pengeluaran Barang
            """)
            inputPilih = pypi.inputInt(prompt="Pilih index: ", lessThan=3)
            if inputPilih == 1:
                inputConfirm = pypi.inputYesNo('Delete data?(y/n) ')
                if inputConfirm =="yes":
                    del dataBarang[inputId]
                    sql = "DELETE FROM barang WHERE id=%s"
                    kursor.execute(sql, [inputId])
                    koneksi.commit()                    
                    print("Data is successfully deleted!")
            else:
                inputQtyOut = pypi.inputInt(prompt="Input jumlah barang yg akan dikeluarkan: ",max= dataBarang[inputId][-3])
                inputKategori = str(input("Kategori pengeluaran barang: "))
                inputConfirm = pypi.inputYesNo(f'Barang {dataBarang[inputId][0]} sebanyak {inputQtyOut} dikeluarkan data?(y/n) ')
                if inputConfirm =="yes":
                    dataBarang[inputId][-3] -= inputQtyOut
                    sql = "UPDATE barang set quantity_barang=%s WHERE id=%s"
                    kursor.execute(sql, [dataBarang[inputId][-3],inputId])
                    koneksi.commit() 

                    key = f"out-{len(dataPengeluaran.keys())+1}"
                    values = [key,inputId,inputKategori,inputQtyOut,datetime.date.today().strftime("%Y/%m/%d")]
                    dataPengeluaran[key] = values[1:]
                    sql = "INSERT INTO pengeluaran VALUES (%s,%s,%s,%s,%s)"
                    kursor.execute(sql, values)
                    koneksi.commit()  
                    print("Data is successfully out!")
        delete()

    def delete_supplier():
        printFormatTable(dataSupplier)
        inputId = pypi.inputStr(prompt="Pilih id supplier yg ingin dihapus: ",blockRegexes=["header","HEADER"])

        if inputId not in dataSupplier.keys():
            print("The data you are looking for does not exist!")
            delete()
        else:
            printDict= {"header": dataSupplier["header"] ,inputId : dataSupplier[inputId]}
            printFormatList(printDict)
            inputConfirm = pypi.inputYesNo('Delete data?(y/n) ')
            if inputConfirm =="yes":
                del dataSupplier[inputId]
                print("Data is successfully deleted!")
            delete()

    inputMenuDelete = pypi.inputInt(prompt='Pilih menu (1-3): ', lessThan=4)
    if inputMenuDelete == 1: delete_barang()
    elif inputMenuDelete == 2: delete_supplier()
    else: main()

def main():
    print("""
    Pilih menu yang akan dijalankan:
        1. Tampil
        2. Tambah
        3. Ubah
        4. Hapus
        5. Exit
    """)

    fetchData()
    menu = pypi.inputInt(prompt='Pilih menu (1-5): ', lessThan=6)
    if menu == 1: read()
    elif menu == 2: add()
    elif menu == 3: update()
    elif menu == 4: delete()
    else: sys.exit()

if __name__ == '__main__':
    main()