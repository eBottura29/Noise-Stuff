import pygame
from pg_utils import *
from PIL import Image, ImageFilter
from threading import Thread

# Vector2 Setup
vector2 = Vector2()
vector2.init_vectors()

# Vector3 Setup
vector3 = Vector3()
vector3.init_vectors()

# Colors Setup
colors = Color()
colors.init_colors()

# Initialize PyGame
pygame.init()

# Set up the screen for display
SCREEN = pygame.display.set_mode(RESOLUTION, pygame.FULLSCREEN if FULLSCREEN else 0)
pygame.display.set_caption(WINDOW_NAME)

clock = pygame.time.Clock()
delta_time = 0.0


def noise():
    r1, r2, r3 = random.random(), random.random(), random.random()
    value = int(random.randint(0, 255) * r1 / r2 + r3)
    return clamp(value, 0, 255), clamp(value, 0, 255), clamp(value, 0, 255)


def amplify(value, amplitude):
    value = (value / 128 - 1) * amplitude
    value = int((value + 1) * 128)
    return clamp(value, 0, 255), clamp(value, 0, 255), clamp(value, 0, 255)


def add_noise(color1, color2, amount):
    value = color1[0] + color2[0] * amount
    value = int(value)
    return clamp(value, 0, 255), clamp(value, 0, 255), clamp(value, 0, 255)


def run(radii):
    """
    Main function to generate noise textures, apply filters, and layer them for multiple radii.
    Handles the image creation, manipulation, and saving using PIL and PyGame.

    :param radii: List of radii to use for Gaussian blur during noise processing.
    """
    noise_layers = []  # List to store noise layers for each radius
    filename = "noise"  # Base filename for saving images

    # Create a new image using PIL for the initial noise texture
    img = Image.new(mode="RGB", size=(WIDTH, HEIGHT))
    pixels = img.load()  # Pixel access object for the first image

    t = time.time()  # Start timing for performance measurement

    # Generate the initial noise texture
    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = noise()  # Generate a random noise color
            pixels[x, y] = color  # Set the pixel in the PIL image

    print(f"Done generating initial noise in {time.time() - t} ms")

    # Apply each radius blur and amplification to create multiple layers
    for index, r in enumerate(radii):
        t = time.time()  # Reset timer

        # Apply a Gaussian blur to the current noise image
        img_blurred = img.filter(ImageFilter.GaussianBlur(r))
        pixels_blurred = img_blurred.load()

        # Amplify the blurred noise texture
        for y in range(HEIGHT):
            for x in range(WIDTH):
                pixels_blurred[x, y] = amplify(pixels_blurred[x, y][0], r / 2)

        # Re-apply blur after amplification
        img_blurred = img_blurred.filter(ImageFilter.GaussianBlur(r))

        # Save the blurred noise image
        img_blurred.save(f"{filename}_blurred_radius_{r}.png")

        print(
            f"Done blurring and amplifying image with radius {r} in {time.time() - t} ms"
        )

        noise_layers.append(img_blurred)  # Append this blurred image as a layer

    # Create an image for the final combined noise texture
    final_img = Image.new(mode="RGB", size=(WIDTH, HEIGHT))
    pixels_final = final_img.load()

    # Combine all blurred noise layers into one final image
    for y in range(HEIGHT):
        for x in range(WIDTH):
            combined_color = (0, 0, 0)  # Initialize the combined color to black
            for layer in noise_layers:
                color1 = pixels_final[x, y]  # Get the current combined color
                color2 = layer.getpixel((x, y))  # Get the color from the current layer
                combined_color = add_noise(color1, color2, 1)
            pixels_final[x, y] = combined_color  # Update the final image pixel
            SCREEN.set_at(
                (x, y), combined_color
            )  # Update PyGame screen with the combined color

    final_img.save(f"{filename}_layered_combined.png")  # Save the combined noise image

    print(f"Done layering all images in {time.time() - t} ms")


def main():
    global delta_time

    running = True
    get_ticks_last_frame = 0.0

    radii = [10, 20, 30]
    thread = Thread(target=run, args=(radii,))
    thread.start()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        pygame.display.flip()

        get_ticks_last_frame, delta_time = manage_frame_rate(
            clock, get_ticks_last_frame
        )

    thread.join()
    pygame.quit()


if __name__ == "__main__":
    main()
