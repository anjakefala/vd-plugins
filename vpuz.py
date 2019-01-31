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
        self.addRow(puzobj)


CrosswordSheet.addCommand('X', 'open-clues', 'vd.push(CluesSheet("clues_"+cursorRow.title, source=cursorRow))')


class GridSheet(Sheet):
    pass


class CluesSheet(Sheet):
    rowtype = 'clues'

    columns = [
            Column('clue_number', getter=lambda col, row: row[0]),
            Column('clue', getter=lambda col, row: row[1])
            ]

    @asyncthread
    def reload(self):
        import crossword

        puzobj = self.source
        puzzle = crossword.from_puz(puzobj)

        self.rows = []

        for number, clue in puzzle.clues.across():
            cluenum = 'A' + str(number)
            self.addRow((cluenum, clue))

        for number, clue in puzzle.clues.down():
            cluenum = 'D' + str(number)
            self.addRow((cluenum, clue))
