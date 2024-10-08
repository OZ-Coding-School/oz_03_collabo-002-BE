import datetime
import hashlib
import hmac
import os
import urllib

import requests


def get_hash(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


def create_signed_headers(headers):
    signed_headers = []

    for k in sorted(headers):
        signed_headers.append("%s;" % k)

    return "".join(signed_headers)[:-1]


def create_standardized_headers(headers):
    signed_headers = []

    for k in sorted(headers):
        signed_headers.append("%s:%s\n" % (k, headers[k]))

    return "".join(signed_headers)


def create_standardized_query_parameters(request_parameters):
    standardized_query_parameters = []

    if request_parameters:
        for k in sorted(request_parameters):
            standardized_query_parameters.append(
                "%s=%s" % (k, urllib.quote(request_parameters[k], safe=""))
            )

        return "&".join(standardized_query_parameters)
    else:
        return ""


class ObjectStorage:
    def __init__(self):
        self.region = "kr-standard"
        self.endpoint = "https://kr.object.ncloudstorage.com"
        self.host = "kr.object.ncloudstorage.com"
        self.access_key = os.environ.get("NCP_ACCESS_KEY")
        self.secret_key = os.environ.get("NCP_SECRET_KEY")

        self.payload_hash = "UNSIGNED-PAYLOAD"
        self.hashing_algorithm = "AWS4-HMAC-SHA256"
        self.service_name = "s3"
        self.request_type = "aws4_request"

        self.time_format = "%Y%m%dT%H%M%SZ"
        self.date_format = "%Y%m%d"

    def _create_credential_scope(self, date_stamp):
        return (
            date_stamp
            + "/"
            + self.region
            + "/"
            + self.service_name
            + "/"
            + self.request_type
        )

    def _create_canonical_request(
        self, http_method, request_path, request_parameters, headers
    ):
        standardized_query_parameters = create_standardized_query_parameters(
            request_parameters
        )
        standardized_headers = create_standardized_headers(headers)
        signed_headers = create_signed_headers(headers)

        canonical_request = (
            http_method
            + "\n"
            + request_path
            + "\n"
            + standardized_query_parameters
            + "\n"
            + standardized_headers
            + "\n"
            + signed_headers
            + "\n"
            + self.payload_hash
        )

        return canonical_request

    def _create_string_to_sign(self, time_stamp, credential_scope, canonical_request):
        string_to_sign = (
            self.hashing_algorithm
            + "\n"
            + time_stamp
            + "\n"
            + credential_scope
            + "\n"
            + hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        )

        return string_to_sign

    def _create_signature_key(self, date_stamp):
        key_date = get_hash(("AWS4" + self.secret_key).encode("utf-8"), date_stamp)
        key_string = get_hash(key_date, self.region)
        key_service = get_hash(key_string, self.service_name)
        key_signing = get_hash(key_service, self.request_type)
        return key_signing

    def _create_authorization_header(
        self, headers, signature_key, string_to_sign, credential_scope
    ):
        signed_headers = create_signed_headers(headers)
        signature = hmac.new(
            signature_key, string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        return (
            self.hashing_algorithm
            + " "
            + "Credential="
            + self.access_key
            + "/"
            + credential_scope
            + ", "
            + "SignedHeaders="
            + signed_headers
            + ", "
            + "Signature="
            + signature
        )

    def _sign(self, http_method, request_path, headers, time, request_parameters=None):
        time_stamp = time.strftime(self.time_format)
        date_stamp = time.strftime(self.date_format)

        credential_scope = self._create_credential_scope(date_stamp)
        canonical_request = self._create_canonical_request(
            http_method, request_path, request_parameters, headers
        )
        string_to_sign = self._create_string_to_sign(
            time_stamp, credential_scope, canonical_request
        )
        signature_key = self._create_signature_key(date_stamp)

        headers["authorization"] = self._create_authorization_header(
            headers, signature_key, string_to_sign, credential_scope
        )

    def put_object(
        self,
        bucket_name,
        object_name,
        file_data,
        acl="public-read",
        request_parameters=None,
    ):
        http_method = "PUT"

        time = datetime.datetime.utcnow()
        time_stamp = time.strftime(self.time_format)

        headers = {
            "x-amz-date": time_stamp,
            "x-amz-content-sha256": self.payload_hash,
            "x-amz-acl": acl,
            "host": self.host,
        }

        request_path = "/%s/%s" % (bucket_name, object_name)

        self._sign(http_method, request_path, headers, time, request_parameters)

        request_url = self.endpoint + request_path
        r = requests.put(
            request_url, headers=headers, params=request_parameters, data=file_data
        )

        return r.status_code, request_url

    def delete_object(self, object_url, request_parameters=None):
        http_method = "DELETE"

        time = datetime.datetime.utcnow()
        time_stamp = time.strftime(self.time_format)
        headers = {
            "x-amz-date": time_stamp,
            "x-amz-content-sha256": self.payload_hash,
            "host": self.host,
        }

        request_path = object_url.split("https://kr.object.ncloudstorage.com")[-1]
        self._sign(http_method, request_path, headers, time, request_parameters)
        r = requests.delete(object_url, headers=headers, params=request_parameters)

        return r.status_code
