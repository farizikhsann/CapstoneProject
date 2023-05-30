import pyinputplus as pypi
import copy
import datetime
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
    
    #Executing and Fetching
    for query in kueri:
        kursor.execute(query)
        rows = kursor.fetchall()

        #Throw rows to dict and updating row as python format
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

#Print as list form
def printFormatList(data):
    cloneData = copy.deepcopy(data)
    
    #Inserting key into value in order to printed key out
    for keys, values in cloneData.items():
        if keys != "header":
            values.insert(0,keys)

    #Printing column then value
    for key, value in cloneData.items():
        if key != "header":
            print("\n".join([f"{cloneData['header'][i]}: {v}" for i, v in enumerate(value)]))
        print()

#Print as table form
def printFormatTable(data):
    cloneData = copy.deepcopy(data)

    #Inserting key into value in order to printed key out
    for keys, values in cloneData.items():
        if keys != "header":
            values.insert(0, keys)

    #Calculation
    maxWidths = [max(len(str(row[i])) for row in cloneData.values()) for i in range(len(cloneData["header"]))] #collect each max row widths per column
    format_string = ' | '.join(['{{:<{}}}'.format(width) for width in maxWidths]) #Create fotmat whitespace length size and joining with separator
    line_length = sum(maxWidths) + 3 * (len(maxWidths) - 1) #Calculate the sum of the row that generates the maximum row width

    #Print the formats
    print('-' * line_length)
    print(format_string.format(*cloneData["header"]))
    print('-' * line_length)
    for keys, values in cloneData.items(): 
        if keys != "header":
            print(format_string.format(*values))
    print('-' * line_length)

#Check availability storage capacity by comparing with goods amount
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

def sortingExpired(date=''):

    def calculateExpiredDay(date):
        today = datetime.date.today()
        date = datetime.datetime.strptime(date, "%Y/%m/%d").date()
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
        
    if len(date):
        return calculateExpiredDay(date)
    
    date_list = [] #Contains id,name,exp_date
    for key, value in dataBarang.items():
        if key != "header":
            date_list.append([key,value[0],value[-4]])

    n = len(date_list)
    for i in range(n - 1):
        for j in range(n - i - 1): 
            if date_list[j][2] > date_list[j + 1][2]:
                date_list[j], date_list[j + 1] = date_list[j + 1], date_list[j]

    for i,date in enumerate(date_list):
        date.append(calculateExpiredDay(date[-1]))
        dataStatusExpired[date[0]] = date[1:]

def read():
    print("""
    Pilih menu:
        1. Tampil Semua Data Barang
        2. Cari Barang Berdasarkan Nama
        3. Tampil Semua Data Supplier
        4. Cari Supplier Berdasarkan Nama
        5. Tampil Data Kapasitas Storage
        6. Tampil Data Pengeluaran Barang
        7. Tampil Status Expired Barang
        8. Back to Menu
    """)

    def findBarang():
        inputNama = pypi.inputStr(prompt="Input nama barang untuk dicari: ").lower()
        
        listBarang = [key for key,nama in dataBarang.items() if nama[0].lower() == inputNama]
        if len(listBarang) == 0:
            print("Data does not exist!")
            read()
        printFormatList({"header": dataBarang["header"] ,listBarang[0] : dataBarang[listBarang[0]]})
    
    def findSupplier():
        inputNama = pypi.inputStr(prompt="Input nama supplier untuk dicari: ").lower()

        listSupplier = [key for key,nama in dataSupplier.items() if nama[0].lower() == inputNama]
        if len(listSupplier) == 0:
            print("Data does not exist!")
            read()
        printFormatList({"header": dataSupplier["header"] ,listSupplier[0]: dataSupplier[listSupplier[0]]})
    
    inputMenuRead = pypi.inputInt(prompt='Pilih menu (1-8): ', lessThan=9)
    
    if inputMenuRead == 1:
        if len(dataBarang.keys()) < 2:
            print("Data was empty, fill the data please!")
            read() 
        printFormatTable(dataBarang)
    elif inputMenuRead == 2: 
        if len(dataBarang.keys()) < 2:
            print("Data was empty, fill the data please!")
            read() 
        findBarang()
    elif inputMenuRead == 3: 
        if len(dataSupplier.keys()) < 2:
            print("Data was empty, fill the data please!")
            read() 
        printFormatTable(dataSupplier)
    elif inputMenuRead == 4: 
        if len(dataSupplier.keys()) < 2:
            print("Data was empty, fill the data please!")
            read() 
        findSupplier()
    elif inputMenuRead == 5: 
        if len(dataStorage.keys()) < 2:
            print("There is no storage data")
            read()
        printFormatTable(availableStorage())
    elif inputMenuRead == 6: 
        if len(dataPengeluaran.keys()) < 2:
            print("There is no outbound goods data")
            read()
        printFormatTable(dataPengeluaran)
    elif inputMenuRead == 7:
        if len(dataBarang.keys()) < 2:
            print("Goods data was empty, fill the goods data please!")
            read()
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
        inputId = pypi.inputStr("Buat id barang: ")
        if inputId[:4] != 'brg-':
                inputId = f'brg-{inputId}'

        if inputId in dataBarang.keys():
            print("Data already exist")
            add() 
            
        else:
            inputNama = pypi.inputStr("Input nama barang: ",default=' ')
            inputTglBeli = pypi.inputDate(prompt='Input tgl beli: ').strftime("%Y/%m/%d")
            inputHarga = pypi.inputInt(prompt='Input harga barang: ',greaterThan=0)
            inputExpired = pypi.inputDate(prompt='Input tgl expired barang: ').strftime("%Y/%m/%d")
            if sortingExpired(inputExpired) == '| EXPIRED |':
                print("The item was expired! cannot be save!")
                add()

            printFormatTable(availableStorage())
            inputQuantity = pypi.inputInt(prompt='Input quantity barang: ',greaterThan=0)

            #filtering storage yg kapasitas memenuhi dari qty
            validStorage =  [keys for keys in availableStorage(inputQuantity).keys() if keys != "header"]
            if len(validStorage) < 1:
                print("Semua kapasitas penyimpanan tidak cukup utk brg ini!")
                add()
            
            printFormatTable(availableStorage(inputQuantity))
            inputLokasi =  pypi.inputChoice(prompt="Pilih id lokasi barang: ",choices= validStorage,blank=True)
            printFormatTable(dataSupplier)
            if len(dataSupplier.keys()) < 2:
                print("Supplier data was empty, fill the data please!")
                add()
            inputSupplier = pypi.inputStr(prompt="Pilih supplier by ID: ")

            if inputSupplier not in dataSupplier.keys() :
                inputCondSupp = pypi.inputYesNo(prompt='Data supplier tidak ditemukan apakah ingin menambahkan data supplier?(y/n) ')
                if inputCondSupp == "yes": 
                    inputSupplier = add_supplier("add_barang")
                
                print("Data failed to save due to the supplier not being assigned!")
                add()
            inputSave = pypi.inputYesNo(prompt='Apakah data barang ingin disimpan?(y/n) ')
            if inputSave =="yes":
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
        inputId = pypi.inputStr(prompt="Buat id supplier: ")
        if inputId[:5] != 'supp-':
            inputId = f'supp-{inputId}'

        if inputId in dataSupplier.keys():
            print("Data already exist")
            add()
        else:
            inputNama = pypi.inputStr(prompt="Input nama supplier: ")
            inputAlamat = pypi.inputStr(prompt="Input alamat supplier: ")
            inputKontak = pypi.inputInt(prompt="Input kontak supplier: ")
            inputSave =pypi.inputYesNo('Apakah data supplier ingin disimpan?(y/n) ')

            if inputSave == "yes":
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
            inputConfirm = pypi.inputYesNo('Continue update?(y/n) ')
            if inputConfirm == "yes":
                inputNama = pypi.inputStr(prompt="Ubah nama barang: ")
                inputTglBeli = pypi.inputDate(prompt='Ubah tgl beli: ').strftime("%Y/%m/%d")
                inputHarga = pypi.inputInt(prompt='Ubah harga barang: ',greaterThan=0)
                inputExpired = pypi.inputDate(prompt='Ubah tgl expired barang: ').strftime("%Y/%m/%d")
                inputQuantity = pypi.inputInt(prompt='Ubah quantity barang: ',greaterThan=-1)
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
            inputNama = pypi.inputStr(prompt="Input nama supplier: ")
            inputAlamat = pypi.inputStr(prompt="Input alamat supplier: ")
            inputKontak = pypi.inputInt(prompt="Input kontak supplier: ")

            inputConfirm = pypi.inputYesNo('Continue update?(y/n) ')
            if inputConfirm == "yes":
                values = [ inputNama, inputAlamat, inputKontak,inputId]
                dataSupplier[inputId] = values[:-2]

                sql = "UPDATE supplier SET nama=%s, alamat=%s, kontak=%s WHERE id=%s"
                kursor.execute(sql, values)
                koneksi.commit()
                print("Data is successfully updated!")
                update()
            else: update()

    if inputMenuUbah == 1:
        if len(dataBarang.keys()) < 2:
            print("Data was empty, fill the data please!")
            update()
        update_barang()
    elif inputMenuUbah == 2: 
        if len(dataSupplier.keys()) < 2:
            print("Data was empty, fill the data please!")
            update()
        update_supplier()
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
                inputKategori = pypi.inputStr(prompt="Kategori pengeluaran barang: ")
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
    if inputMenuDelete == 1: 
        if len(dataBarang.keys()) < 2:
            print("Data was empty, fill the data please!")
            delete()
        delete_barang()
    elif inputMenuDelete == 2: 
        if len(dataSupplier.keys()) < 2:
            print("Data was empty, fill the data please!")
            delete()
        delete_supplier()
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