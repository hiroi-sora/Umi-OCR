from .output_txt import OutputTxt
from .output_txt_plain import OutputTxtPlain
from .output_txt_individual import OutputTxtIndividual
from .output_md import OutputMD
from .output_jsonl import OutputJsonl
from .output_csv import OutputCsv


Output = {
    "txt": OutputTxt,
    "txtPlain": OutputTxtPlain,
    "txtIndividual": OutputTxtIndividual,
    "md": OutputMD,
    "jsonl": OutputJsonl,
    "csv": OutputCsv,
}
