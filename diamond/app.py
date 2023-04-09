import os
import subprocess

from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import storage


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/diamond", methods=["GET", "POST"])
def diamond():
    sequence = """>K00001.1
MGAVSSNAPTSRALVLEAPRRLVVRELAVPEIGADDALVRVEACGLCGTDHEQYTGALSG
GFAFVPGHETVGIIEAIGPQAARRWGVAAGDRVAVEVFQSCRQCPNCLAGEYRRCERHGL
ADMYGFIPVDRAPGLWGGYAEYQYLAPDSMVLPVPAGLDPAVASLFNPLGAGIRWGATLP
GTGAGDVVAVLGPGVRGLCAAAAAKEAGAGFVMLTGLGPRDADRLALAPQFGVDLAVDVA
ADDPVAALHDATGGLADVVVDVTAKAPAAFAQAIALARPAGTVVVAGTRGLGAGAPGFSP
DLVVFKELRILGALGVDATAYRAALALLASGRYPFESLPRRCVRLDDAEELLATMAGERA
GLPPVHGVLTP
>K00001.2
MLPRYYEFYNPVKVLSGEHALENLPYEMAHLHAKRPILLTNQQLVEVGLTRILQDALRGS
DLTIAAQYTEIPQDSSIHVVNAAGRVFREAGCDSIIALGGGSVIDTAKGLRVLIGQETDD
IMQYMGADILQPKRRVPLAVVPTTAGTGSEATLVAVIAHPERQVKMEFVSHHLLPDLAVL
DPRMTRSLPPRITASTGMDALVHAIEGYTSIQRNPLSDAYAWAAIELIREYLPRAVANGQ
DTEARLAMANAALMAGAAFSNAMVGLVHAIGHAVGGVARVAHGDAMAILLPHVMEYNLDM
LSDRYGRLLLALAGPEVYAATPDNVRGSQAIAVVRAFAERLHQACGLPLRLRDVGVTEAQ
LPAIARTTMNDGALLMNAKEAGPDDVMQILRKAF
"""
    if request.method == "POST":
        sequence = request.json["sequence"]

    result = subprocess.run(
        "diamond blastp -d words.dmnd --outfmt 6 qseqid stitle evalue pident --max-target-seqs 1 --evalue 1e-4",
        shell=True,
        input=sequence,
        capture_output=True,
        text=True,
        check=False,
    )
    return jsonify({"returncode": result.returncode, "out": result.stdout, "err": result.stderr})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
