keydir="certs"
mkdir -p $keydir
cd "$keydir"

# CA cert and private key
openssl genrsa -out ca.key 2048
openssl req -x509 -new -nodes -key ca.key -days 10000 -out ca.crt -subj "/CN=admission_ca"

echo "################### Copy below string to caBundle ###################"
cat ca.crt | base64
echo "################### End caBundle ####################################"

# private key for the webhook server
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=nsat.hooks.svc" -config ../server.conf

#verify the csr
# openssl req -in nst.csr -noout -text

#Create certificate using CSR and Root CA
# openssl x509 -req -days 365 -in nst.csr -signkey ca.key -out nst.crt -extfile ../ext.cnf -extensions req_ext
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 10000 -extensions v3_req -extfile ../server.conf

 
cp server.crt servercrt.pem
echo "################### Copy below string to servercrt.pem in secret ###################"
cat servercrt.pem | base64
echo "################### End servercrt.pem for secret ###################################"

cp server.key serverkey.pem
echo "################### Copy below string to serverkey.pem in secret ###################"
cat serverkey.pem | base64
echo "################### End serverkey.pem for secret ###################################"

