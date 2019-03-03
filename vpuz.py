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


CrosswordSheet.addCommand(ENTER, 'open-clues', 'vd.push(CluesSheet("clues_"+cursorRow.title, source=cursorRow))')

class GridSheet(Sheet):
    rowtype = 'gridrow'

    @asyncthread
    def reload(self):

        grid = self.source

        ncols = len(grid[0])
        self.columns = [ColumnItem('', i, width=2) for i in range(ncols)]

        for row in grid:
            row = list(row)
            self.addRow(row)


class CluesSheet(Sheet):
    rowtype = 'clues'

    columns = [
            Column('clue_number', getter=lambda col, row: row[0]),
            Column('clue', getter=lambda col, row: row[1]),
            Column('answer', getter=lambda col, row: row[2])
            ]

    @asyncthread
    def reload(self):
        import crossword

        puzobj = self.source
        puzzle = crossword.from_puz(puzobj)

        grid_dict = dict(list(zip(string.ascii_uppercase, string.ascii_uppercase)))
        grid = []

        # grid
        for r, row in enumerate(puzzle):
            rowstr = ""
            for c, cell in enumerate(row):
                if puzzle.block is None and cell.solution == '.':
                    rowstr += '#' # block_char
                elif cell.solution == puzzle.block:
                    rowstr += '#' # block_char
                elif cell.solution == ':':
                    rowstr += '_' # open_char
                elif cell == puzzle.empty:
                    rowstr += '.' # unknown_char
                else:
                    n = r * puzobj.width + c
                    ch = cell.solution
                    rowstr += grid_dict[ch]

            grid.append(rowstr)

        # answers
        answers = {}
        for posdir, posnum, answer in self.iteranswers(grid):
            answers[posdir[0] + str(posnum)] = answer

        # clues

        self.rows = []

        for number, clue in puzzle.clues.across():
            cluenum = 'A' + str(number)
            self.addRow((cluenum, clue, answers.get(cluenum, ''), grid))

        for number, clue in puzzle.clues.down():
            cluenum = 'D' + str(number)
            self.addRow((cluenum, clue, answers.get(cluenum, ''), grid))

    def iteranswers(self, grid):
        for direction, clue_num, answer, r, c in self.iteranswers_full(grid):
            yield direction, clue_num, answer

    def iteranswers_full(self, grid):
        NON_ANSWER_CHARS = ['#', '_']
        rebus = {}
        for c in string.ascii_letters:
            rebus[c] = c.upper()

        clue_num = 1

        for r, row in enumerate(grid):
            for c, cell in enumerate(row):
                new_clue = False
                if self.cell(r, c - 1, grid) in NON_ANSWER_CHARS:
                    ncells = 0
                    answer = ""
                    while self.cell(r, c + ncells, grid) not in NON_ANSWER_CHARS:
                        cellval = self.cell(r, c + ncells, grid)
                        answer += rebus.get(cellval, cellval)
                        ncells += 1

                    if ncells > 1:
                        new_clue = True
                        yield "A", clue_num, answer, r, c

                if self.cell(r - 1, c, grid) in NON_ANSWER_CHARS:
                    ncells = 0
                    answer = ""
                    while self.cell(r + ncells, c, grid) not in NON_ANSWER_CHARS:
                        cellval = self.cell(r + ncells, c, grid)
                        answer += rebus.get(cellval, cellval)
                        ncells += 1

                    if ncells > 1:
                        new_clue = True
                        yield "D", clue_num, answer, r, c

                if new_clue:
                    clue_num += 1


    def cell(self, r, c, grid):
        if r < 0 or c < 0 or r>= len(grid) or c >= len(grid[0]):
            return '#' # BLOCK_CHAR
        return grid[r][c]

CluesSheet.addCommand('X', 'open-grid', 'vd.push(GridSheet("grid", source=cursorRow[3]))')
