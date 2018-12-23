import sys
import requests
import time


host = "127.0.0.1:5006"


def menu():
    print("======MENU======")
    print("1. Transfer")
    print("2. Cek Saldo")
    print("3. Cek Total Saldo")
    print("4. Ping")
    print("5. Register")
    print("press q to quit")

def req(url, payload):
    r = requests.post(url, json=payload)
    return r.json()

def transfer(user_id, nilai, tujuan):
    url = "http://{}/ewallet/transfer".format(tujuan)
    data = req(url, {"user_id": user_id, "nilai": nilai})
    return data

def cek_saldo(user_id, tujuan):
    url = "http://{}/ewallet/getSaldo".format(tujuan)
    data = req(url, {"user_id": user_id})
    return data

def cek_total_saldo(user_id):
    url = "http://{}/ewallet/getTotalSaldo".format(host)
    data = req(url, {"user_id": user_id})
    return data

def substract_saldo(user_id, nilai):
    url = "http://{}/substractSaldo".format(host)
    data = req(url, {"user_id": user_id, "nilai": nilai})
    return data

def register(user_id, nama, tujuan):
    url = "http://{}/ewallet/register".format(tujuan)
    data = req(url, {"user_id": user_id, "nama": nama})
    return data

def ping():
    url = "http://{}/ewallet/ping".format(host)
    data = req(url, {})
    return data

def main():
    menu()
    while True:
        inp = str(input("Insert menu [1-5]: "))
        if inp == "1":

            print("Masukkan user_id:")
            user_id = str(input())
            print("Masukkan nilai:")
            nilai = int(input())
            print("Masukkan IP Node Tujuan: (cth: 172.0.0.212)")
            tujuan = str(input())
            saldo = cek_saldo(user_id, tujuan)

    
            if saldo["saldo"] == -1:
                print("Masukkan nama: ")
                nama = str(input())
                r = register(user_id, nama, tujuan)
            elif saldo["saldo"] < -1:
                print("Terjadi error pada sistem silahkan coba lagi")
                menu()
                continue
            
            saldo_me = cek_saldo(user_id, host)

            
            if saldo_me["saldo"] > -1:
                if saldo_me["saldo"] < nilai:
                    print("Saldo tidak boleh kurang dari nilai transfer")
                    menu()
                    continue

            trf = transfer(user_id, nilai, tujuan)
            if trf["transferReturn"] > -1:
                substract_saldo(user_id, nilai)
            else:
                print("Terjadi kegagalan dalam transfer")
                menu()
                continue

            print("Berhasil melakukan transfer")
            time.sleep(2)
            menu()
        elif inp == "2":
            print("Masukkan user_id: ")
            user_id = str(input())
            saldo = cek_saldo(user_id, host)

            if saldo["saldo"] > -1:
                print("Jumlah saldo anda adalah", saldo["saldo"])
            else:
                print("Terjadi kesalahan dalam server")
            menu()

        elif inp == "3":
            print("Masukkan user_id: ")
            user_id = str(input())
            total_saldo = cek_total_saldo(user_id)

            if total_saldo["saldo"] > -1:
                print("Jumlah total saldo anda adalah", total_saldo["saldo"])
            else:
                print("Terjadi kesalahan dalam server")
            menu()
        elif inp == "4":
            pong = ping()
            if pong["pingReturn"] > -1:
                print("PONG!")
                menu()
            else:
                print("Gagal melakukan ping")
                menu()

        elif inp == "5":
            print("Masukkan user_id: ")
            user_id = str(input())
            print("Masukkan nama: ")
            nama = str(input())
            reg = register(user_id, nama, host)

            if reg["registerReturn"] > -1:
                print("Berhasil melakukan register")
            else:
                print("Gagal melakukan register")
            menu()
        elif inp == "q":
            break

main()