from __future__ import print_function

import os
import sys
import re

from keyvaultlib.key_vault import KeyVaultOAuthClient


# Load function for sys err reporting
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(1)


def ProcessMappingFile(file):
    try:
        _mapping = dict()
        if (file is not None and os.path.isfile(file)):
            with open(file, "r") as openfile:
                for line in openfile.read().splitlines():
                    kv = line.split("=")
                    _mapping.update({kv[0]: kv[1]})
        else:
            raise ValueError("Unable to read mapping file \"{}\"".format(file))
        return _mapping
    except Exception as err:
        eprint("Error processing mapping file => {}".format(err))


def CheckSaveDir(path):
    try:
        # First check if the directory exists
        if path is None or not os.path.exists(os.path.dirname(path)):
            raise ValueError(
                "Directory \"{}\" does not exist".format(os.path.dirname(path)))
        # Second check if directory is writable
        if not os.access(os.path.dirname(path), os.W_OK):
            raise ValueError("Path {} not writable".format(path))
    except Exception as err:
        eprint("Error validating savedir => {}".format(err))


# Define variables used in Program
SECRET_MAPPING = dict()
VAULTNAME = os.getenv('VAULT_NAME')

# Step 1 - Off to the races!
print("Starting azkvinit app...")

# Step 2 - Grab and process mapping file from argv
if (len(sys.argv) < 2):
    eprint("azkvinit requires full path to mapping file")
else:
    SECRET_MAPPING = ProcessMappingFile(sys.argv[1])

# Step 3 - Validate Vault Name is supplied
if VAULTNAME is None:
    eprint("Please define VAULT_NAME env variable")

print("Found {} secrets".format(len(SECRET_MAPPING)))

# Step 4 - Extract the secrets
# Load the MSI OAuth client used to fetch secrets with MSI
try:
    client = KeyVaultOAuthClient(use_msi=True)
except Exception as err:
    eprint("Unable to init AZKV client, please validate you're running in AKS with MSI enabled =>", err)

try:
    for key in SECRET_MAPPING:
        # A Check if the path is valid
        CheckSaveDir(SECRET_MAPPING[key])

        # B Obtain and write out the secret
        with open(SECRET_MAPPING[key], "w") as outfile:
            outfile.write(client.get_secret_with_key_vault_name(VAULTNAME, key))
            outfile.close()
        print("Wrote {}".format(key))
except Exception as err:
    eprint("Error processing secret => {}".format(err))

print("Finished!")
sys.exit(0)
