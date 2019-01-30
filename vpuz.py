from visidata import *

def open_puz(p):
     vs = CrosswordSheet(p.name, source=p)
     return vs

class CrosswordSheet(Sheet):
    rowtype = 'rows' 
    columns = [
            Column('Author', getter=lambda col, row: row.author),
            Column('Copyright', getter=lambda col, row: row.copyright),
            Column('Notes', getter=lambda col, row: row.notes),
            Column('Postscript', getter=lambda col, row: ''.join(x for x in row.postscript if ord(x) >= ord(' '))),
            Column('Preamble', getter=lambda col, row: row.preamble),
            Column('Title', getter=lambda col, row: row.title)
            ]

    @asyncthread
    def reload(self):
        import puz

        self.rows = []

        contents = self.source.open_bytes().read()
        puzobj = puz.load(contents)
        #vs = CluesSheet('clues_'+puzobj.title, source=puzobj)
        #vs.reload()
        #vs.puzobj = puzobj
        self.addRow(puzobj)
#CrosswordSheet.addCommand(ENTER, 'dive-row', 'vd.push(cursorRow)')



class GridSheet(Sheet):
    pass

class CluesSheet(Sheet):

    @asyncthread
    def reload(self):
        import crossword

        puzzle = crossword.from_puz(self.source)

        for r, row in enumerate(puzzle):
            rowstr = []

