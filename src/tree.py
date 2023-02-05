import torch
from torch.autograd import Variable


class Node:
    _symbols = None
    _s2c = None

    def __init__(self, symbol=None, right=None, left=None):
        self.symbol = symbol
        self.right = right
        self.left = left
        self.target = None
        self.prediction = None

    def __str__(self):
        return "".join(self.to_list())

    def __len__(self):
        left = len(self.left) if self.left is not None else 0
        right = len(self.right) if self.right is not None else 0
        return 1 + left + right

    def height(self):
        hl = self.left.height() if self.left is not None else 0
        hr = self.right.height() if self.right is not None else 0
        return max(hl, hr) + 1

    def to_list(self, notation="infix"):
        if notation == "infix" and Node._symbols is None:
            raise Exception("To generate a list of token in the infix notation, symbol library is needed. Please use"
                            "the Node.add_symbols methods to add them, before using the to_list method.")
        left = [] if self.left is None else self.left.to_list(notation)
        right = [] if self.right is None else self.right.to_list(notation)
        if notation == "prefix":
            return [self.symbol] + left + right
        elif notation == "postfix":
            return left + right + [self.symbol]
        elif notation == "infix":
            if len(left) > 0 and len(right) == 0 and Node.symbol_precedence(self.symbol) > 0:
                return [self.symbol] + ["("] + left + [")"]
            elif len(left) > 0 and len(right) == 0 and Node.symbol_precedence(self.symbol) <= 0:
                return ["("] + left + [")"] + [self.symbol]

            if self.left is not None \
                    and -1 < Node.symbol_precedence(self.left.symbol) < Node.symbol_precedence(self.symbol):
                left = ["("] + left + [")"]
            if self.right is not None \
                    and -1 < Node.symbol_precedence(self.right.symbol) < Node.symbol_precedence(self.symbol):
                right = ["("] + right + [")"]
            return left + [self.symbol] + right
        else:
            raise Exception("Invalid notation selected. Use 'infix', 'prefix', 'postfix'.")

    def add_target_vectors(self):
        if Node._symbols is None:
            raise Exception("Encoding needs a symbol library to create target vectors. Please use Node.add_symbols"
                            " method to add a symbol library to trees before encoding.")
        target = torch.zeros(len(Node._symbols)).float()
        target[Node._s2c[self.symbol]] = 1.0
        self.target = Variable(target[None, None, :])
        if self.left is not None:
            self.left.add_target_vectors()
        if self.right is not None:
            self.right.add_target_vectors()

    def loss(self, mu, logvar, lmbda, criterion):
        pred = Node.to_matrix(self, "prediction")
        target = Node.to_matrix(self, "target")
        BCE = criterion(pred, target)
        KLD = (lmbda * -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()))
        return BCE + KLD, BCE, KLD

    def clear_prediction(self):
        if self.left is not None:
            self.left.clear_prediction()
        if self.right is not None:
            self.right.clear_prediction()
        self.prediction = None

    def to_dict(self):
        d = {'s': self.symbol}
        if self.left is not None:
            d['l'] = self.left.to_dict()
        if self.right is not None:
            d['r'] = self.right.to_dict()
        return d

    @staticmethod
    def from_dict(d):
        left = None
        right = None
        if "l" in d:
            left = Node.from_dict(d["l"])
        if 'r' in d:
            right = Node.from_dict(d["r"])
        return Node(d["s"], right=right, left=left)

    @staticmethod
    def symbol_precedence(symbol):
        return Node._symbols[Node._s2c[symbol]]["precedence"]

    @staticmethod
    def to_matrix(tree, matrix_type="prediction"):
        reps = []
        if tree.left is not None:
            reps.append(Node.to_matrix(tree.left, matrix_type))

        if matrix_type == "target":
            reps.append(torch.Tensor([Node._s2c[tree.symbol]]).long())
        else:
            reps.append(tree.prediction[0, :, :])

        if tree.right is not None:
            reps.append(Node.to_matrix(tree.right, matrix_type))

        return torch.cat(reps)

    @staticmethod
    def add_symbols(symbols):
        Node._symbols = symbols
        Node._s2c = {s["symbol"]: i for i, s in enumerate(symbols)}

