#!/bin/env sh

openssl req -x509 -newkey rsa:2048 -sha256 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/C=US/ST=Some-State/L=Detroit/O=cringeBot/OU=education/CN=${DvangoDomain}"
