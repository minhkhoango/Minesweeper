import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """
        count_mines = 0
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count_mines += 1
        return count_mines

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count and self.count != 0:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()
        

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        #mark as move made
        self.moves_made.add(cell)
        #mark as safe
        self.mark_safe(cell)
        #add to knowledge base

        neighbors = set()
        known_mines_count = 0

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) == cell:
                    continue
                if (i, j) in self.safes:
                    continue
                if (i, j) in self.mines:
                    count = count - 1
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:
                    if (i, j) in self.mines:
                        known_mines_count += 1
                    elif (i, j) not in self.mines:
                        neighbors.add((i, j))
        
        adjusted_count = count - known_mines_count

        if neighbors:
            self.knowledge.append(Sentence(neighbors, adjusted_count))

        self.update_knowledge()

    def update_knowledge(self):
        """Update the AI's knowledge base to the mark new cells as safe or as
        mines based on current information"""
        changed = True
        while changed:
            changed = False
            new_mines = set()
            new_safes = set()

            for sentence in self.knowledge:
                known_mines = sentence.known_mines()
                known_safes = sentence.known_safes()

                if known_mines:
                    new_mines.update(known_mines)
                    # update the new set by adding mines we just concluded
                if known_safes:
                    new_safes.update(known_safes)
            
            for mine in new_mines:
                if mine not in self.mines:
                    self.mark_mine(mine)
                    changed = True
                    #update internal knowledge
            
            for safe in new_safes:
                if safe not in self.safes:
                    self.mark_safe(safe)
                    changed = True

            # make sure no knowledge sentence is empty from the reducing of cells above
            self.knowledge = [sentence for sentence in self.knowledge if sentence.cells]

            # creating new logic from existing ones
            for i, sentence1 in enumerate(self.knowledge):
                for sentence2 in self.knowledge[i + 1:]:
                    if sentence1 == sentence2:
                        continue

                    if sentence2.cells.issubset(sentence1.cells) and sentence2.cells:
                        new_cells = sentence1.cells - sentence2.cells
                        new_count = sentence1.count - sentence2.count

                        if new_count >= 0:
                            """add new knowledge"""
                            inferred_sentence = Sentence(new_cells, new_count)
                            if inferred_sentence not in self.knowledge:
                                print("New knowledge: ", inferred_sentence)
                                self.knowledge.append(inferred_sentence)
                                changed = True
        
        print("Current AI KB length: ", self.knowledge)
        print("Mines found: ", self.mines)
        print("Safe cells remaining: ", self.safes - self.moves_made)
        print("==============================================================================")

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for move in self.safes:
            if move not in self.moves_made:
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        moves = {} # dict for moves
        MINES = 8

        #mines left on the board
        nums_mines_left = MINES - len(self.mines)
        #the moves we have left
        spaces_left = (self.height * self.width) - (len(self.mines) + len(self.moves_made))
        if spaces_left == 0:
            return None
        
        basic_prob = nums_mines_left / spaces_left
        #assign every leftover moves with that probability
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.mines and (i, j) not in self.moves_made:
                    moves[(i, j)] = basic_prob

        if not moves:
            #no moves available
            return None
        
        if not self.knowledge:
            #completely random board
            print("The AI is making a random choice based on basic probability")
            return random.choice(list(moves.keys()))
        
        # making a more educated guess
        for sentence in self.knowledge:
            num_cells = len(sentence.cells)
            if num_cells == 0:
                continue

            calculated_prob = sentence.count / num_cells
            # update probability if the new one is higher to be bomb
            for cell in sentence.cells:
                if cell in moves:
                    moves[cell] = max(moves[cell], calculated_prob)

        min_prob = min(moves.values())
        best_moves = [cell for cell, prob in moves.items() if prob == min_prob]
        
        move = random.choice(best_moves)
        print("The AI is making an informed choice based on the lowest mine possibility", move)
        return move

        
                

