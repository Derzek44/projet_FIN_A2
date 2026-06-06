import pygame

from settings import WIDTH, HEIGHT, CARS
from menu_screen import MenuScreen
from car import Car
from sound_manager import SoundManager
from game import Game


def main():
    pygame.init()
    pygame.mixer.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("F1 Racing")

    clock = pygame.time.Clock()

    menu = MenuScreen(screen, clock)
    sound_manager = SoundManager()

    running = True

    while running:
        action = menu.menu_principal()

        if action == "quit":
            running = False

        elif action == "jouer":
            mode = menu.selection_mode()

            if mode == "quit":
                running = False

            elif mode == "back":
                pass

            elif mode == "human":
                choice1 = menu.selection_vehicule(1, CARS)

                if choice1 == "quit":
                    running = False

                elif choice1 == "back":
                    pass

                else:
                    car1 = Car(CARS[choice1]["image"])

                    choice2 = menu.selection_vehicule(2, CARS)

                    if choice2 == "quit":
                        running = False

                    elif choice2 == "back":
                        pass

                    else:
                        car2 = Car(CARS[choice2]["image"])

                        game = Game(
                            screen,
                            clock,
                            car1,
                            car2,
                            sound_manager,
                            mode
                        )

                        result = game.run()

                        if result == "quit":
                            running = False

            elif mode == "ghost":
                choice1 = menu.selection_vehicule(1, CARS)

                if choice1 == "quit":
                    running = False

                elif choice1 == "back":
                    pass

                else:
                    car1 = Car(CARS[choice1]["image"])

                    ghost_choice = menu.selection_vehicule_fantome(CARS)

                    if ghost_choice == "quit":
                        running = False

                    elif ghost_choice == "back":
                        pass

                    else:
                        ghost_car = Car(CARS[ghost_choice]["image"])
                        ghost_file = "ghost_" + CARS[ghost_choice]["name"].replace(" ", "_") + ".json"
                        game = Game(
                            screen,
                            clock,
                            car1,
                            ghost_car,
                            sound_manager,
                            mode,
                            ghost_file
                        )

                        result = game.run()

                        if result == "quit":
                            running = False

    pygame.quit()

if __name__ == "__main__":
    main()