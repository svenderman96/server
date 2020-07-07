import xml.etree.ElementTree as xml
from pathlib import Path
from threading import Thread
import threading
import socket

port = 12345
hostname = socket.gethostname()
host = socket.gethostbyname(hostname)

print('\nIP address: ' + str(host) )
print('Port:       ' + str(port) + '\n')

clients = set()
clients_lock = threading.Lock()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.bind((host, port))
s.listen(3)
th = []

#Create XML file
path=Path()
result = list(path.glob('podaci.xml'))

if len(result) == 0:
    print("Fajl ne postoji,kreiraj fajl unosom prve zemlje.\n\n")
    root = xml.Element("countries")
    c1 = xml.Element("country")
    root.append(c1)

    drzava = input("Unesi naziv drzave: ")
    name = xml.SubElement(c1, "name")
    name.text = drzava

    broj_obolelih = input("Unesi broj obolelih: ")
    oboleli = xml.SubElement(c1, "oboleli")
    oboleli.text = broj_obolelih

    broj_preminulih = input("Unesi broj preminulih: ")
    preminuli = xml.SubElement(c1, "preminuli")
    preminuli.text = broj_preminulih

    broj_izlecenih = input("Unesi broj izlecenih: ")
    izleceni = xml.SubElement(c1, "izleceni")
    izleceni.text = broj_izlecenih

    tree = xml.ElementTree(root)
    with open("podaci.xml", "wb") as files:
        tree.write(files)


def listener(client, address):
    global notWorking
    print("\nAccepted connection from: ", address, '\n')

    with clients_lock:
        clients.add(client)
    try:
        while True:
            data = client.recv(1024)
            if int(data) == 0:
                if onWorking:
                    print('\nData updating...\n')
                else:
                    print("\nSending data...\n")
                    filename = 'podaci.xml'
                    f = open(filename, 'rb')
                    l = f.read(4096)
                    while (l):
                        client.send(l)
                        print('Sent ', repr(l))
                        l = f.read(4096)
                    f.close()

    except ValueError:
        print("\nClient Disconnected\n")


def Update():
    global onWorking
    tree = xml.parse("podaci.xml")
    root = tree.getroot()

    drzava = input("Unesi naziv drzave: ")

    for country in root.findall('country'):
        name = country.find('name').text
        if (name == drzava):
            root.remove(country)

    attrib = {}
    element = root.makeelement('country', attrib)
    root.append(element)

    name = xml.SubElement(element, "name")
    name.text = drzava

    broj_obolelih = input("Unesi broj obolelih: ")
    oboleli = xml.SubElement(element, "oboleli")
    oboleli.text = broj_obolelih

    broj_preminulih = input("Unesi broj preminulih: ")
    preminuli = xml.SubElement(element, "preminuli")
    preminuli.text = broj_preminulih

    broj_izlecenih = input("Unesi broj izlecenih: ")
    izleceni = xml.SubElement(element, "izleceni")
    izleceni.text = broj_izlecenih


    tree = xml.ElementTree(root)
    with open("podaci.xml", "wb") as files:
        tree.write(files)

    zavrsio = input("\nData update finished(press y or Y to confirm or any other key to cancel): ")
    if(zavrsio == 'y' or zavrsio == 'Y'):
        onWorking = False


def ReactOnCase():
    global onWorking
    while True:
        if not onWorking:
            c = input("\nPress W or w to UPDATE data or any other key to continue: ")
            if(c == 'W' or c == 'w') and not onWorking:
                onWorking = True
                print("\nAdmin mode: UPDATE IN PROGRESS\n")

def NewClientsReceivement():
    while True:
        print("\nServer is listening for new connections...\n")
        client ,address = s.accept()
        th.append(Thread(target=listener, args=(client, address)).start())

try:
    global onWorking

    onWorking = False
    th.append(Thread(target=ReactOnCase).start())
    th.append(Thread(target=NewClientsReceivement).start())

    while True:

        if onWorking:
            Update()

except MemoryError:
    s.close()
    print("\nServer cloesd\n")
    exit()