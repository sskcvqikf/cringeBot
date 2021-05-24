if [ -z ${DvangoToken+x} ] || [ -z ${DvangoHost+x} ] || [ -z ${DvangoPort+x} ] || [ -z ${DvangoDomain+x} ]
then
    echo "You have to set DvangoToken, DvangoHost, DvangoPort, DvangoDomain enviroment varibles. Exiting..."
    exit 1
fi

echo "Generating SSL certificates..."
cd cert
. ./create_cert.sh
cd ..

echo "Creating Webhook to https://${DvangoDomain}:${DvangoPort}/${DvangoToken} (with self-signed certificate)..."
curl -F "url=https://${DvangoDomain}:${DvangoPort}/${DvangoToken}" -F "certificate=@./cert/cert.pem" https://api.telegram.org/bot${DvangoToken}/setWebhook

echo "\nAll done! To verify that webhook is set correctly go check getWebhookInfo."
