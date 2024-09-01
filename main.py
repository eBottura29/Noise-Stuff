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
    """
    Generate a random noise color tuple (R, G, B).
    The values are clamped between 0 and 255 to ensure valid color ranges.
    """
    r1, r2, r3 = random.random(), random.random(), random.random()
    value = int(random.randint(0, 255) * r1 / r2 + r3)
    return clamp(value, 0, 255), clamp(value, 0, 255), clamp(value, 0, 255)


def amplify(value, amplitude):
    """
    Amplify the noise value based on an amplitude parameter.
    Adjusts the color intensity based on the provided amplitude.
    """
    value = (value / 128 - 1) * amplitude
    value = int((value + 1) * 128)
    return clamp(value, 0, 255), clamp(value, 0, 255), clamp(value, 0, 255)


def add_noise(color1, color2, amount):
    """
    Combine two noise textures with a specified blending amount.
    The amount determines the influence of the second noise texture.
    """
    value = color1[0] + (color2[0] / 128 - 1) * amount
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

    # Create a new image using PIL for the first noise texture
    img = Image.new(mode="RGB", size=(WIDTH, HEIGHT))
    pixels1 = img.load()  # Pixel access object for the first image

    t = time.time()  # Start timing for performance measurement

    # Generate the initial noise texture
    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = noise()  # Generate a random noise color
            pixels1[x, y] = color  # Set the pixel in the PIL image

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

        noise_layers.append(img_blurred)  # Append this blurred image as a layer

        img_blurred.save(
            f"{filename}_blurred_radius_{r}.png"
        )  # Save the blurred noise image

        print(
            f"Done blurring and amplifying image with radius {r} in {time.time() - t} ms"
        )

    # Create another image for layering the generated noise textures
    layered_img = Image.new(mode="RGB", size=(WIDTH, HEIGHT))
    pixels_layered = layered_img.load()

    # Initialize the final noise to be the same as the initial noise
    for y in range(HEIGHT):
        for x in range(WIDTH):
            combined_color = (0, 0, 0)  # Initialize the combined color
            for layer in noise_layers:
                color1 = pixels1[x, y]
                color2 = layer.getpixel((x, y))
                combined_color = add_noise(color1, color2, 1)
            pixels_layered[x, y] = combined_color
            SCREEN.set_at((x, y), combined_color)

    layered_img.save(
        f"{filename}_layered_combined.png"
    )  # Save the combined noise image

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
