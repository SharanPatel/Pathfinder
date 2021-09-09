import pygame
import math
import time
from queue import PriorityQueue

pygame.font.init()

WIDTH = 600
HEIGHT = 750
ROWS = 30
FONT = pygame.font.SysFont("Helvetica", 16)
FONTSMALL = pygame.font.SysFont("Helvetica", 14)
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (233,196,106)
GREEN = (244,162,97)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
TURQUOISE = (64, 224, 208)
ORANGE = (42,157,143)
TURQUOISE = (231,111,81)

BLACK = (38,70,83)
PRIMARY = RED
GREY = BLACK


class Spot:
    def __init__(self, row, col, width, totalRows, color, editable=True):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = color
        self.neighbors = []
        self.width = width
        self.totalRows = totalRows
        self.editable = editable

    def getPos(self):
        return self.row, self.col

    def isClosed(self):
        return self.color == RED

    def isOpen(self):
        return self.color == GREEN

    def isBarrier(self):
        return self.color == BLACK

    def isStart(self):
        return self.color == ORANGE

    def isEnd(self):
        return self.color == TURQUOISE

    def isEditable(self):
        return self.editable == True

    def reset(self):
        self.color = WHITE

    def makeStart(self):
        self.color = ORANGE

    def makeClosed(self):
        self.color = RED

    def makeOpen(self):
        self.color = GREEN

    def makeBarrier(self):
        self.color = BLACK

    def makeEnd(self):
        self.color = TURQUOISE

    def makePath(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def updateNeighbors(self, grid):
        self.neighbors = []
        if self.row < self.totalRows - 1 and not grid[self.row + 1][self.col].isBarrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].isBarrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.totalRows - 1 and not grid[self.row][self.col + 1].isBarrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].isBarrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])


def buildGrid(width, rows):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            if j == 0 or j == rows - 1 or i == 0 or i == rows - 1:
                color = BLACK
                isEditable = False
            spot = Spot(i, j, gap, rows, color, isEditable)
            grid[i].append(spot)
            color = WHITE
            isEditable = True

    return grid


def drawWindow(win, grid, width, height, rows, margin):
    win.fill(WHITE)
    gap = width // rows
    bannerH = height - width

    # draw spots
    for row in grid:
        for spot in row:
            spot.draw(win)

    # draw lines
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

    # draw buttons
    pygame.draw.rect(win, PRIMARY, (width / 3, width + margin, width / 3 - margin, bannerH / 2 - margin * 1.5))
    pygame.draw.rect(win, PRIMARY, (width / 3, width + bannerH / 2 + margin / 2, width / 3 - margin, bannerH / 2 - margin * 1.5))
    pygame.draw.rect(win, PRIMARY, (width / 3 * 2, width + margin, width / 3 - margin, bannerH / 2 - margin * 1.5))
    pygame.draw.rect(win, PRIMARY, (width / 3 * 2, width + bannerH / 2 + margin / 2, width / 3 - margin, bannerH / 2 - margin * 1.5))


    pygame.draw.rect(win, PRIMARY, (margin, width + bannerH / 2 + margin / 2, width / 3 - margin * 2, (bannerH / 2 - margin * 2.5) / 2))
    pygame.draw.rect(win, PRIMARY, (margin, width + bannerH / 4 * 3 + margin / 4, width / 3 - margin * 2, (bannerH / 2 - margin * 2.5) / 2))

    text = FONT.render("Dijkstra", 1, BLACK)
    win.blit(text, (width / 2 - 30, width + bannerH / 4 - 8))
    text = FONT.render("Greedy BFS", 1, BLACK)
    win.blit(text, (width / 2 - 50, width + bannerH / 4 * 3 - 10))
    text = FONT.render("A Star", 1, BLACK)
    win.blit(text, (width / 6 * 5 - 25, width + bannerH / 4 - 8))
    text = FONT.render("Convergent Swarm", 1, BLACK)
    win.blit(text, (width / 6 * 5 - 70, width + bannerH / 4 * 3 - 10))

    text = FONTSMALL.render("Clear Search", 1, BLACK)
    win.blit(text, (width / 6 - 45, width + bannerH / 8 * 5 - 8))
    text = FONTSMALL.render("Clear All", 1, BLACK)
    win.blit(text, (width / 6 - 28, width + bannerH / 8 * 7 - 10))

    text = FONTSMALL.render("# of Iterations: " + str(iterations), 1, BLACK)
    win.blit(text, (margin, width + margin + bannerH / 6 * 0))
    text = FONTSMALL.render("Total Time: " + str(elapsedTime) + "s", 1, BLACK)
    win.blit(text, (margin, width + margin + bannerH / 6 * 1))
    text = FONTSMALL.render("Path Distance: " + str(path) + " units", 1, BLACK)
    win.blit(text, (margin, width + margin + bannerH / 6 * 2))
    pygame.display.update()


def getClickPosition(x, y, rows, width):
    gap = width // rows
    row = x // gap
    column = y // gap

    return row, column


def hDistance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def eDistance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt(pow((x2 - x1), 2) + pow((y2 - y1),2))


def reconstructPath(cameFrom, start, end, draw):
    global path
    while end in cameFrom:
        end = cameFrom[end]
        path += 1
        if end != start:
            end.makePath()
        draw()

def greedyBFSAlgorithm(draw, grid, start, end):
    global iterations, elapsedTime
    counter = 0
    elapsedTime = 0
    openSet = PriorityQueue()
    openSet.put((0, counter, start))
    openSetTemp = {start}
    cameFrom = {}

    fScore = {spot: float("inf") for row in grid for spot in row}
    fScore[start] = eDistance(start.getPos(), end.getPos())

    while not openSet.empty():
        elapsedTime = round(time.time() - startTime, 3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        node = openSet.get()[2]
        openSetTemp.remove(node)

        if node == end:
            reconstructPath(cameFrom, start, end, draw)
            end.makeEnd()
            return True

        for neighbor in node.neighbors:
            iterations += 1
            if not neighbor.isClosed() and not neighbor.isStart():
                cameFrom[neighbor] = node
                fScore[neighbor] = eDistance(neighbor.getPos(), end.getPos())
                if neighbor not in openSetTemp:
                    counter += 1
                    openSet.put((fScore[neighbor], counter, neighbor))
                    openSetTemp.add(neighbor)
                    neighbor.makeOpen()

        draw()
        if node != start:
            node.makeClosed()
    return False

def aStarAlgorithm(draw, grid, start, end):
    global iterations, elapsedTime
    counter = 0
    elapsedTime = 0
    openSet = PriorityQueue()
    openSet.put((0, counter, start))
    openSetTemp = {start}
    cameFrom = {}

    gScore = {spot: float("inf") for row in grid for spot in row}
    fScore = {spot: float("inf") for row in grid for spot in row}

    gScore[start] = 0
    fScore[start] = hDistance(start.getPos(), end.getPos())

    while not openSet.empty():
        elapsedTime = round(time.time() - startTime, 3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        node = openSet.get()[2]
        openSetTemp.remove(node)

        if node == end:
            reconstructPath(cameFrom, start, end, draw)
            end.makeEnd()
            return True

        for neighbor in node.neighbors:
            iterations += 1
            tempGScore = gScore[node] + 1

            if tempGScore < gScore[neighbor]:
                cameFrom[neighbor] = node
                gScore[neighbor] = tempGScore
                fScore[neighbor] = tempGScore + hDistance(neighbor.getPos(), end.getPos())
                if neighbor not in openSetTemp:
                    counter += 1
                    openSet.put((fScore[neighbor], counter, neighbor))
                    openSetTemp.add(neighbor)
                    neighbor.makeOpen()

        draw()

        if node != start:
            node.makeClosed()
    return False

def swarmAlgorithm(draw, grid, start, end):
    global iterations, elapsedTime
    counter = 0
    elapsedTime = 0
    openSet = PriorityQueue()
    openSet.put((0, counter, start))
    openSetTemp = {start}
    cameFrom = {}

    gScore = {spot: float("inf") for row in grid for spot in row}
    fScore = {spot: float("inf") for row in grid for spot in row}

    gScore[start] = 0
    fScore[start] = eDistance(start.getPos(), end.getPos())

    while not openSet.empty():
        elapsedTime = round(time.time() - startTime, 3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        node = openSet.get()[2]
        openSetTemp.remove(node)

        if node == end:
            reconstructPath(cameFrom, start, end, draw)
            end.makeEnd()
            return True

        for neighbor in node.neighbors:
            iterations += 1
            tempGScore = gScore[node] + 1

            if tempGScore < gScore[neighbor]:
                cameFrom[neighbor] = node
                gScore[neighbor] = tempGScore
                fScore[neighbor] = math.sqrt(tempGScore) + math.sqrt(eDistance(neighbor.getPos(), end.getPos()))
                if neighbor not in openSetTemp:
                    counter += 1
                    openSet.put((fScore[neighbor], counter, neighbor))
                    openSetTemp.add(neighbor)
                    neighbor.makeOpen()

        draw()

        if node != start:
            node.makeClosed()
    return False

def dijkstraAlgorithm(draw, grid, start, end):
    global iterations, elapsedTime
    counter = 0
    elapsedTime = 0
    openSet = PriorityQueue()
    openSet.put((0, counter, start))
    openSetTemp = {start}
    cameFrom = {}

    gScore = {spot: float("inf") for row in grid for spot in row}
    gScore[start] = 0

    while not openSet.empty():
        elapsedTime = round(time.time() - startTime, 3)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        node = openSet.get()[2]
        openSetTemp.remove(node)

        if node == end:
            reconstructPath(cameFrom, start, end, draw)
            end.makeEnd()
            return True

        for neighbor in node.neighbors:
            iterations += 1
            tempGScore = gScore[node] + 1

            if tempGScore < gScore[neighbor]:
                cameFrom[neighbor] = node
                gScore[neighbor] = tempGScore
                if neighbor not in openSetTemp:
                    counter += 1
                    openSet.put((gScore[neighbor], counter, neighbor))
                    openSetTemp.add(neighbor)
                    neighbor.makeOpen()

        draw()

        if node != start:
            node.makeClosed()
    return False


def clearVars():
    global iterations, path, elapsedTime
    iterations = 0
    elapsedTime = 0
    path = 0


def main(win, width, height, rows):
    global iterations, startTime, path, elapsedTime
    clearVars()
    margin = 6
    grid = buildGrid(width, rows)
    bannerH = height - width

    startPoint = None
    endPoint = None

    isRunning = True
    while isRunning:
        drawWindow(win, grid, width, height, rows, margin)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False

            if pygame.mouse.get_pressed()[0]:  # LEFT
                x, y = pygame.mouse.get_pos()
                if x < width and y < width:
                    row, col = getClickPosition(x, y, rows, width)
                    spot = grid[row][col]
                    if not startPoint and spot != endPoint and not spot.isBarrier():
                        startPoint = spot
                        spot.makeStart()

                    elif not endPoint and spot != startPoint and not spot.isBarrier():
                        endPoint = spot
                        spot.makeEnd()

                    elif spot != endPoint and spot != startPoint:
                        spot.makeBarrier()

                elif width / 3 < x < width < y < height and startPoint and endPoint: # algorithms
                    clearVars()
                    for i in range(rows):
                        for j in range(rows):
                            if grid[i][j].color == RED or grid[i][j].color == GREEN or grid[i][j].color == PURPLE:
                                grid[i][j].color = WHITE

                    for row in grid:
                        for spot in row:
                            spot.updateNeighbors(grid)
                    startTime = time.time()

                    if width / 3 < x < width / 3 * 2 and width < y < width + bannerH / 2:
                        dijkstraAlgorithm(lambda: drawWindow(win, grid, width, height, rows, margin), grid, startPoint,endPoint)
                    elif width / 3 * 2 < x < width < y < width + bannerH / 2:
                        aStarAlgorithm(lambda: drawWindow(win, grid, width, height, rows, margin), grid, startPoint,endPoint)
                    elif width / 3 < x < width / 3 * 2 and width + bannerH / 2 < y < height:
                        greedyBFSAlgorithm(lambda: drawWindow(win, grid, width, height, rows, margin), grid, startPoint,endPoint)
                    else:
                        swarmAlgorithm(lambda: drawWindow(win, grid, width, height, rows, margin), grid, startPoint,endPoint)

                elif x < width / 3 and width + bannerH / 2 < y < width + bannerH / 4 * 3: # clear search
                    clearVars()
                    for i in range(rows):
                        for j in range(rows):
                            if grid[i][j].color == RED or grid[i][j].color == GREEN or grid[i][j].color == PURPLE:
                                grid[i][j].color = WHITE

                elif x < width / 3 and width + bannerH / 4 * 3 < y < height:  # clear all
                    clearVars()
                    startPoint = None
                    endPoint = None
                    grid = buildGrid(width, rows)

            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                x, y = pygame.mouse.get_pos()
                if x < width and y < width:
                    row, col = getClickPosition(x, y, rows, width)
                    spot = grid[row][col]

                    if spot == startPoint:
                        startPoint = None
                    elif spot == endPoint:
                        endPoint = None

                    if spot.isEditable():
                        spot.reset()


main(WIN, WIDTH, HEIGHT, ROWS)
