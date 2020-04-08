import pygame
from pygame.mask import from_surface
import neat
import time
import os
import random
pygame.font.init()

#loading images and setting thee screen
WIN_WIDTH=500
WIN_HEIGHT=800

# for the generation
GEN=0

BIRD_IMAGES=[pygame.transform.scale2x(pygame.image.load(os.path.join("images-fb","bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("images-fb","bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("images-fb","bird3.png")))]

PIPE_IMAGE=pygame.transform.scale2x(pygame.image.load(os.path.join("images-fb","pipe.png")))
BASE_IMAGE=pygame.transform.scale2x(pygame.image.load(os.path.join("images-fb","base.png")))
BG_IMAGE=pygame.transform.scale2x(pygame.image.load(os.path.join("images-fb","bg.png")))

# loading the fonts
STAT_FONT=pygame.font.SysFont("comicsans",50)

DRAW_LINES=True

class Bird:
    IMGS=BIRD_IMAGES
    # when we want to tilt the bird up and down it nose pointing that way.
    MAX_ROTATION=25
    # rotingn frames each time we want to move teh bird
    ROT_VEL=20
    # how long we show each bird animation
    ANIMATION_TIME=5
    def __init__(self,x,y):
        #def __int__(self,x,y):
        self.x=x
        self.y=y
        # deciding how much the image is tilting
        self.tilt=0
        # Deciding the physics of our bird when we jump or we g down
        self.tick_count=0
        # our velocity
        self.vel=0
        # deciding the height of the bord
        self.height=self.y
        # deciding the amount of images of the bird being displayed
        self.image_count=0
        # setting the initial image of the bird as the first one.
        self.img=self.IMGS[0]

    # setting a function which will be useful when we will jump
    def jump(self):
        # the inital velocity for our bird which will be ini upwards direction
        self.vel = -10.5
        # deciding how many times the bird will jump.Initial will be zero
        self.tick_count=0
        # initial height for the bird jump
        self.height=self.y

    #calling this method to move the frames in our game
    def move(self):
        # a tick happend and we jumped once
        self.tick_count+=1
        # displacement, this will be the distance our bird will be moving with each jump.
        # This will keep decreasing with each jump.
        d=self.vel*(self.tick_count)+1.5*self.tick_count**2

        # limiting thee move down vel to 16 if it is more.
        if d>=16:
            d=16

        # setting the jump up vel to be more than we get from above
        if d<0:
            d-=2

        # setting the y post of the bord.
        self.y=self.y+d

        # checking if we are moving above and tilting
        # the bird only when it has stopped moving up and begun to retrace back down.
        if d<0 or (self.y<(self.height+50)):

            # making sure the bird is not tilted the wrong way.
            # also checking where to tilt the bird (up or down)
            if self.tilt<self.MAX_ROTATION:
                self.tilt=self.MAX_ROTATION
            else:

                # rotating the bord completely downwards
                if self.tilt>-90:
                    self.tilt=self.ROT_VEL

    # win represents the window on which we draw the bord.
    def draw(self,win):
        # tracking how many times we have shown the image.
        self.image_count+=1

        # checking what image of the bord to be shown at what time
        if self.image_count<self.ANIMATION_TIME:
            self.img=self.IMGS[0]
        elif self.image_count<self.ANIMATION_TIME*2:
            self.img=self.IMGS[1]
        elif self.image_count<self.ANIMATION_TIME*3:
            self.img=self.IMGS[2]
        elif self.image_count<self.ANIMATION_TIME*4:
            self.img=self.IMGS[1]
        elif self.image_count == self.ANIMATION_TIME*4+1:
            self.img=self.IMGS[0]
            self.image_count = 0

        # checking if the bird going down then setting the image acc.
        if self.tilt<= -80:
            self.img=self.IMGS[1]

            # making the bird to not skip a frame when it goes back up again.
            self.image_count=self.ANIMATION_TIME*2

        # rotating the image about its center
        rotated_image=pygame.transform.rotate(self.img,self.tilt)
        # moving the bord also after the rotation to avoid looking weird
        new_rect=rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x,self.y)).center)

        # drawing the image on win
        win.blit(rotated_image,new_rect.topleft)

    # this function is helpful in determining the collisions.
    # We get a 2D list of pixels which will be used to see if we have collision or not.
    def get_mask(self):
        return from_surface(self.img)


class Pipe:
    # gap between the pipes
    GAP=200
    # velocity with which the pipes will move towards the bird
    VEL=5

    def __init__(self,x):
        self.x=x
        self.height=0

        # keeping the position of the pipe
        self.top=0
        self.bottom=0
        self.PIPE_TOP=pygame.transform.flip(PIPE_IMAGE,False,True)
        self.PIPE_BOTTOM=PIPE_IMAGE

        # seeing if the bird has passed the pipe.
        # this also determines the drawing of another pipe on the screen
        self.passed=False
        self.set_height()

    # setting the height of the pipe
    def set_height(self):
        self.height=random.randrange(50,450)
        self.top=self.height-self.PIPE_TOP.get_height()
        self.bottom=self.height+self.GAP

    # moving the pipe in the left direction
    def move(self):
        self.x-=self.VEL

    # drawing the required things
    def draw(self,win):
        win.blit(self.PIPE_TOP,(self.x,self.top))
        win.blit(self.PIPE_BOTTOM,(self.x,self.bottom))

    # checking if the collision take place or not
    def collide(self,bird):
        # getting the mash for the bird
        bird_mask=bird.get_mask()
        # creating the mask for our pipes
        top_mask=from_surface(self.PIPE_TOP)
        bottom_mask=from_surface(self.PIPE_BOTTOM)

        # offset means the distance between the masks
        top_offset=(self.x-bird.x, self.top-round(bird.y))
        bottom_offset=(self.x-bird.x, self.bottom-round(bird.y))

        # finding if the masks collide i.e. finding the point of collision,
        # returns None if no collision
        b_point=bird_mask.overlap(bottom_mask,bottom_offset)
        t_point=bird_mask.overlap(top_mask,top_offset)

        if t_point or b_point:
            return True
        return False

# class to set the base moving
class Base:
    VEL=5
    WIDTH=BASE_IMAGE.get_width()
    IMG=BASE_IMAGE

    def __init__(self,y):
        self.y=y
        self.x1=0
        self.x2=self.WIDTH

    def move(self):
        self.x1-=self.VEL
        self.x2-=self.VEL

        if self.x1+self.WIDTH < 0:
            self.x1=self.x2+self.WIDTH

        if self.x2+self.WIDTH < 0:
            self.x2=self.x1+self.WIDTH

    def draw(self,win):
        win.blit(self.IMG,(self.x1,self.y))
        win.blit(self.IMG,(self.x2,self.y))


# drawing the stuff
def draw_window(win,birds,pipes,base,score,gen,pipe_ind):
    # drawing the background image
    win.blit(BG_IMAGE,(0,0))

    # drawing pipes on the screen
    for pipe in pipes:
        pipe.draw(win)

    # rendering our score
    text=STAT_FONT.render("Score: "+str(score),1,(0,0,0))
    win.blit(text,(WIN_WIDTH-10-text.get_width(),10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen - 1), 1, (255, 255, 255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(score_label, (10, 50))

    # drawing base on the screen
    base.draw(win)



    # drawing the bord along with the tilt and rotations
    for bird in birds:
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255, 0, 0),
                                 (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2),
                                 (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width() / 2, pipes[pipe_ind].height),
                                 3)
                pygame.draw.line(win, (255, 0, 0),
                                 (bird.x + bird.img.get_width() / 2, bird.y + bird.img.get_height() / 2), (
                                 pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width() / 2,
                                 pipes[pipe_ind].bottom), 3)
            except:
                pass
        bird.draw(win)
    # updating the display
    pygame.display.update()


def main(genomes,config):

    global GEN
    GEN+=1

    # by this we keep the track of the neural nets controlling the bird and the genomes.
    nets=[]
    ge=[]

    birds=[]

    for _,g in genomes:
        # it is a deep learning model
        net=neat.nn.FeedForwardNetwork.create(g,config)
        nets.append(net)
        birds.append(Bird(230,350))
        # setting the initial fitness to zero
        g.fitness=0
        ge.append(g)

    base=Base(730)
    score=0
    pipes=[Pipe(600)]
    win=pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))

    # Setting the time to slow if we we want bird to fall down slowly
    #clock=pygame.time.Clock()
    # variable to be changed to stop
    run=True

    # this will be helpful in running.
    while run:
        # slowing the clock
        #clock.tick(30)

        # checking for an event
        for event in pygame.event.get():
            # for closing the game
            if event.type==pygame.QUIT:
                run=False
                pygame.quit()
                quit()

        # this will be used for checking which pipe to look at.
        # initially looking at the 0 pipe and as soon as we have passed it look at the next one then.
        # this will also be the deciding factor for quitting the game
        pipe_ind=0
        if len(birds)>0:
            if len(pipes)>1 and birds[0].x > pipes[0].PIPE_TOP.get_width():
                pipe_ind=1
        else:
            run=False
            break

        # for moving the birds
        # we will pass the inputs to Nn which will check the outputs
        # and if the output is greater that 0.5 make the bird jump
        for x, bird in enumerate(birds):
            bird.move()
            # providing the fitness value less as this loop will run 30
            # times a second and if more value is there bird will touch the top screen
            ge[x].fitness+=0.1

            # send bird location, top pipe location and bottom pipe location and
            # determine from network whether to jump or not
            output = nets[x].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))
            # making the bird jump
            if output[0]>0.5:
                bird.jump()
        # moving the bird
        #bird.move()

        # used for drawing pipes on the screen
        add_pipe=False
        # list which will contain the removed pipes
        rem=[]
        for pipe in pipes:
            for x,bird in enumerate(birds):
                # checking for the collision
                if pipe.collide(bird):
                    # if a bird hit a pipe then its fitness level will be decreased
                    ge[x].fitness-=1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                # used for drawing another pipe on the screen
                if not pipe.passed and pipe.x<bird.x:
                    pipe.passed=True
                    add_pipe=True
            # removing the pipe once it has passed the left corner of screen
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                    rem.append(pipe)

            pipe.move()

        # updating the score and adding a new pipe
        if add_pipe:
            score+=1
            print(score)
            for g in ge:
                g.fitness+=5
            pipes.append(Pipe(600))

        # removing the pipes in our rem list
        for r in rem:
            pipes.remove(r)

        # making the bird die when it hits top or bottom
        for x,bird in enumerate(birds):
            if bird.y+bird.img.get_height()>=730 or bird.y<0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        # moving the base
        base.move()

        # drawing the bird
        draw_window(win,birds,pipes,base,score,GEN,pipe_ind)





# inputs for the algorithm will be bird y posi, top pipe, bottom pipe
# outputs will be jump or not
# activation function will be tan(h)
# initial no. of neurons or bird which will be starting in the beginning.
# fitness function:- evaluating how the birds are, the bird who reach the farthest scores the best.
# max generation means the maximum value for which we will try before terminating and trying again.

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    # we have specified the things which wehave mentioned in our config file.

    p = neat.Population(config)
    # generation the population

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # this will give ous some stats about the fitness and stuff

    winner=p.run(main,50)
    # 50 defines the generations which we want to run.
    # this is the fitness function which we will be specifying



    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__=="__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)