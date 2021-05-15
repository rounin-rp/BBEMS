import ipfshttpclient

def uploadFileToIPFS(filename):
    return_data = [False,]
    try:
        client = ipfshttpclient.connect()
        result = client.add(filename)
        print(filename)
        if result:
            return_data[0] = True
            metadata = {}
            metadata['FileName'] = result['Name']
            metadata['Size'] = result['Size']
            metadata['Hash'] = result['Hash']
            return_data.append(metadata)
        else:
            return_data.append({})
    except:
        return_data.append({})
        print("IPFS encountered an error")
    return return_data


def downloadFileFromIPFS(filename,address):
    try:
        client = ipfshttpclient.connect()
        binFile = client.cat(address)
        filename = "DOWNLOADED_"+filename
        file = open(filename,'wb')
        file.write(binFile)
        file.close()
        print(f"file has been successfully downloaded as {filename}")
    except:
        print("IPFS encountered an error maybe you are not connected to IPFS")
