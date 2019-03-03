from visidata import *
import pydicom
from pydicom.data import get_testdata_files

def open_dcm(s):
    return DicomSheet(s.name, source=s)

class DicomSheet(Sheet):
    rowtype = 'metadata'

    columns = [
            ColumnAttr('tag'),
            ColumnAttr('keyword'),
            ColumnAttr('VR', width=0),
            ColumnAttr('value')
            ]

    nKeys = 1

    def reload(self):
        self.rows = []

        dicom_data = pydicom.dcmread(self.source.resolve())

        for metadata in dicom_data.iterall():
            self.addRow(metadata)


