from visidata import *
import pydicom
from pydicom.data import get_testdata_files

def open_dcm(s):
    return DicomSheet(s.name, source=s)

class DicomSheet(Sheet):
    rowtype = 'metadata'

    def reload(self):
        self.rows = []
        self.columns = []

        dicom_data = pydicom.dcmread(self.source.resolve())

        for metadata in dicom_data.iterall():
            self.addRow(metadata)

        for c in PyobjColumns(self.rows[0]):
            self.addColumn(c)

        self.setKeys([self.column("tag")])
        for col_name in 'descripWidth is_raw is_undefined_length maxBytesToDisplay showVR file_tell is_retired VM'.split():
            self.column(col_name).hide()
