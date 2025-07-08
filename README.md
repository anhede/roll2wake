# WakeUpBro - A DnD alarm clock
## :game_die: Tutorial on how to build a gamified DnD Alarm Clock

**Waking up is not fun**
**Alarms are not fun**
**Let's fix that**

---

I'm **Josef Anhede** (ja225sg) and today we'll be building **the world's most fun alarm clock.**

The project is split into five key steps.
1. Dev Environment (1hr) 
2. Hardware & Wiring (4hr)
3. Device & component programming (1hr)
4. Server / Client setup (2hr)
5. Visualization (2hr)

In total, expect this to take around a full day of work. If you already know your way around microcontrollers, and some basic networking, it will be quicker. :zap:

If you wish to also 3D print the parts, expect another full days of work, since you'll have to adjust my .blend file to fit your specific buttons, potentiometers, and wait for all parts to print.

## Objective
I've always had trouble waking up, and I know many others have as well. It's all too easy to stop the alarm and go back to sleep. Using hardcore alarm apps like [Alarmy](https://alar.my/en) works for some, but me? I just end up deleting the app to stop the alarm and continue sleeping.

If you're like me, and want the best alarm clock to actually wake up, you're in the right place.

Our goal is to create an alarm clock that **actually wakes you up**, while also **being fun.** How do we achieve this? With a DnD game of course! :game_die: 

Each morning, you will have to complete a DnD style choose your own adventure game to stop the alarm. This is great because it's both fun, but it's also engaging. It forces you to actually think and be present when waking up. 

The stories are not long, they're completed in 2~5 minutes, but that's enough for your brain to go from sleep mode, to awake mode! :star-struck: 

To make sure that each morning carries a unique story, the scenario, choices and setting are all generated at runtime using state of the art LLMs. I've added support for both the OpenAI API (ChatGPT), and the Anthropic API (Claude). This makes for a novel and engaging experience each time.

Finally, we will add some smart Sleep tracking statistics which highlights the times you go to bed, for how long you sleep, when you wake up, and how long it takes for you to turn off the alarm. These stats allow you to make informed decisions in the future of when you ought to go to bed, and set your alarm.

## Material
Almost all of the materials used in the project come from the Freenove Super Starter Kit (Pico W) available at either [Amazon SE](https://www.amazon.se/-/en/Freenove-Raspberry-Included-588-Page-Detailed) or their [US/CAD/AUS website](https://store.freenove.com/products/fnk0063?variant=43034491289798). 

The only components not included here is the larger 4x20 LCD screen, an I2C-interface card compatible with it, and the 3V active piezoelectric buzzer. I sourced mine from Electrokit ([Screen](https://www.electrokit.com/lcd-4x20-tecken-jhd204a-stn-bla/vitled), [I2C-interface](https://www.electrokit.com/i2c-interface-for-lcd), [Buzzer](https://www.electrokit.com/piezohogtalare-aktiv)) but there are many others available.
> :grey_exclamation: You can use any size screen, the project makes no assumption on the size and is built to be compatible with any display size. I prefer 4x20 since it leads to less scrolling of long texts.

|                                                                                        Component | Description / Use                                                                                                                                                     | Price & Source     |
| ------------------------------------------------------------------------------------------------:| --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:------------------ |
|                     Pico W Kit <img src="https://hackmd.io/_uploads/SybyKY-Vxe.jpg" width="200"> |                                                                                                                                                                       | 499kr @ Amazon.se  |
|                                                                                10K Potentiometer | Used as scrolling input, e.g. scrolling text, or selecting items on a radial menu.                                                                                    | from Kit           |
|                                                                                       Pushbutton | Used as push/held input, e.g. moving forward through menus, toggling alarm state.                                                                                     | from Kit           |
|                                                                       Ultrasonic Distance Sensor | By default the LCD backlight is off as to not disturb your sleep, if you wish to see the time, you may wave over this sensor and it lights up the screen in response. | from Kit           |
|                                                                             Neopixel 8RGB Circle | Cirucular RGB strip for visualizing dice rolls.                                                                                                                       | from Kit           |
| 3V Active Piezoelectric Buzzer <img src="https://hackmd.io/_uploads/rJZVFFZNll.jpg" width="100"> | The sound-generating component which makes the alarm. You may program whichever pattern you wish onto it.                                                             | 32kr @ Electrokit  |
|                4x20 LCD Screen <img src="https://hackmd.io/_uploads/HyEZYY-4lg.jpg" width="100"> | The text-displaying screen.                                                                                                                                           | 179kr @ Electrokit |
|              I2C LCD Interface <img src="https://hackmd.io/_uploads/rymQYKWEel.jpg" width="100"> | Reduces the pin count to connect the 4x20 LCD screen to only 4 pins.                                                                                                  | 42kr @ Electrokit  |


## Hardware setup and wiring
Now we can wire it all up. Below is a schematic of the whole diagram.

We use four colors to make it clear what wire does what:
- <span style="background-color: red; color: white; padding: 2px 6px; border-radius: 4px;"><strong>Red</strong></span> ~ 3.3V  
- <span style="background-color: black; color: white; padding: 2px 6px; border-radius: 4px;"><strong>Black</strong></span> ~ Ground  
- <span style="background-color: orange; color: white; padding: 2px 6px; border-radius: 4px;"><strong>Yellow</strong></span> ~ 5V *from VBUS*  
- <span style="background-color: blue; color: white; padding: 2px 6px; border-radius: 4px;"><strong>Blue</strong></span> ~ GP/I2C/ADC Signals

> :warning:  To provide adequate power for the display, **you must hook up the controller to a 5V power source**. For initial setup a normal laptop/PC USB is perfect, but for portability for the finished project I recommend a 5V DC Power adapter used for phones. **Make sure such an adapter does not exceed 5V**:exclamation:

![roll2wake_circuit](https://hackmd.io/_uploads/BJDrO5qrxl.png)

> I personally chose to use a "breadboard-style" prototyping board, but it's perfectly replaceable with the breadboard included in the Freenove Kit! If using a normal breadboard, the 5V top line is not available, draw the VCC wire for the LCD directly to the 5V VBUS instead.

## Computer Setup
You've got the hardware all connected, and you're almost ready to go. Now let's setup a development environment in VS Code and copy the code over to our Pico W.

### 1. Setup VSCode

1. Download and install [VS Code](https://code.visualstudio.com/) for your operating system.
2. Install the **MicroPico** extension for VSCode.

That's it for the IDE setup, now we need to load the correct firmware to your Pico W before we can start working.

### 2. Set Up Your Pico

1. Hold the **BOOTSEL** button on your Pico and connect it to your computer via USB.
2. Release the button once it's connected.
3. The Pico should mount as a storage device, in Windows you will se it as a new device in File Explorer.
4. Upload the UF2 file according to [this guide](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) to install MicroPython on your Pico 

After this you can open VS Code and MicroPico should be able to detect that you're connected to your Pico W. You can see the status of the connection in the status bar at the bottom of the window.

### 3. Upload project to the Pico

1. Start by cloning the repo, open any terminal and run:
    ```bash
    git clone https://github.com/anhede/roll2wake/
    ```
2. Open the `roll2wake` folder in VS Code.
3. Upload the project by choosing **All Commands** > **Upload project to Pico**.

> :bulb: After making changes to your code, they must be reuploaded to the pico using the same **Upload project to Pico** command.


### You're Done!

Your project is now uploaded to the Raspberry Pi Pico. Let's do a small dive into how the code work, and how it's structured.

## Programming the Pico

The code is split into multiple modular parts. This is to allow code reuse for future projects, and make it easy to customize and add your own functionalities.

- **Components** is my MicroPython package with classes for each of the components used. These components take the desired *pin(s)* as input, and expose an easy-to-use, high-level interface.
    >:heavy_check_mark: Each component file has a small example on how to use it. Run all components to try them out and check that your wiring works!
-  **Routines** are small generic *subprograms* meant for use in a larger stateful application. E.g. a menu screen which reads the potentiometer as a dial, and allows selection of different options, or a routine which allows to scroll through text, and ends when pressing the pushbutton.
- **Client** is another small MicroPython package of this project containing classes for handling Wifi and communication with our **Server**, as well as NTP Time sync for setting the alarm's time automatically.
- **Server** is the Flask app meant to run on a server. I use my Raspberry Pi 4, but any normal laptop or PC works as well. The server code is written in normal Python and won't run on our Pico. It serves the client with LLM responses for the DnD adventures, and it also runs **sqlite** and **Dash** for storing and displaying the statistics from 
    > :information_source: If your wiring is different from mine, make sure to update the correct pins in `components/pins.py`.


### Components
Below is an example of how to use our simplest component, the pushbutton.

At the bottom of the **pushbutton** class you’ll find a runnable demo. Just give it a GPIO pin (and optionally a custom hang-time in milliseconds) and then it's ready to use. Notice the easy to use method `button.is_pressed()`. There is a similar method `button.is_held()` for checking if it's currently held or not.

```python
if __name__ == "__main__":
    button = PushButton(15, min_click_ms=100)
    led = Pin("LED", Pin.OUT)
    led.off()

    while True:
        if button.is_pressed():
            led.toggle()
            print("Button pressed! LED is now",
                  "ON" if led.value() else "OFF")
        time.sleep_ms(50)
```

Run it on your board by pressing `Run` at the bottom of VSCode in the *MicroPico* toolbar


All other components follow this same pattern:
1. **Instantiate** with the correct pin (and options)
2. **Call** the high-level method(s) you need (`is_pressed`, `message`, `distance_mm` etc.)
3. **Run** the example at the bottom to see it in action and check your wiring.


### Routines

Routines are reusable, self-contained functions that stitch together your components to provide higher-level user interactions. Each routine takes the components it uses as inputs.

The `choice_menu` routine simply takes a list of the available `prompts` as strings. These are what will be displayed on the screen, and can be chosen by rotating the potentiometer. It also takes all other components which it uses to provide a working menu.

At the bottom of the **choicemenu** file you’ll find an example usage:

```python
if __name__ == "__main__":
    import time
    neopix  = NeopixelCircle(pin=16, brightness=1)
    screen  = Screen(20, 21)
    pot     = Potentiometer(28)
    pushb   = PushButton(15)
    prompts = ["Attack", "Run away", "Drink love\npotion", "Alt F4"]

    idx = choice_menu(prompts, neopix, screen, pot, pushb)
    screen.message(f"Selected: {prompts[idx]}")
    neopix.clear()
```

Run it on your board by pressing `Run` at the bottom of VSCode in the MicroPico toolbar.


All routines work similarly, they expect take both the components, and routine-specific parameters as inputs.

#### Main Routine
Running the special `main.py` routine located in the root of the project runs the actual alarm clock. You cannot run it yet, since we must first configure the Wifi and API client and server. So let's go ahead!

### **Client**
The project comes with two classes, `Client` and `WifiClient`. The `WifiClient` connects to the network, and uses **NTP** to sync time.

Besides receiving Stories from the LLM on the server, the client also publishes sleep statistics to the server. Each time the alarm goes off, a *wakeup* event is sent to the server. Additionally, each time the user interacts with the alarm clock, e.g. toggling the alarm, or changing the alarm time, the client sends an *interaction* event to the server. The interaction events are limited to one every minute, and as such the rate of transmission is extremely low and doesn't effect performance or power draw.

The server can infer sleep periods by finding the time between the latest *interaction* event, and earliest *wakeup* event.

#### Configuring the WifiClient
To get the `WifiClient` working, add a text file named `wifi_settings.txt` containing your SSID and password to the project's `client` folder.

`client/wifi_settings.txt`
```
YOUR_SSID_HERE,YOUR_PASSWORD_HERE
```
After this you may run the `WifiClient.py` file to verify that is successfully connects to the network and syncs using NTP.

#### Configuring the Client
The only thing you need to modify to get your `Client` working is adjust the `base_url` argument in the classes constructor. In `client.py`, adjust the following line to reflect your server.
```python
client = Client("http://192.168.1.234:5000") # Replace with your server IP
```

### **Server**
#### Platform

The server has three responsibilities:
1. Act as an intermediary between the Pico W and the LLM API to generate the DnD stories. 
2. Store sleep statistics from the Alarm clock.
3. Visualize the sleep statistics on a web dashboard.

We will use **Flask** to *accomplish all of these three steps in a single application*. One could use other Cloud-hosted platforms for easily transmitting, storing and visualizing data, but I chose not to use any external services.

This makes the project more **cohesive**. There is a single git project, *written only in Python*, which handles everything. You can even reuse classes and constants defined in the `.py` files between the Server and the Client since they're part of the same project.

It also gives us total freedom in our approach, how we want to visualize and store the data, and makes it easy to expand on as a Open Source project.

#### Flask
Flask is a lightweight and low-code solution for implementing web applications. We use a REST-API with GET and POST routes for getting LLM stories, and posting statistics. Setting up a response for a specific url is as easy as follows:
```python
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'storyteller-api'
    })
```

#### OpenAI / Anthropic
To communicate with the LLMs, we use the `openai` and `anthropic` packages. We have implemented one class for each API, which can be freely chosen between. 
> They both derive from an abstract `llm` class, so they're easy to swap out, or even add a third LLM provider if you wish.

Check this example to see how easy they are to use:

```python
openai_api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# Models
llm_gpt = OpenAILLM(
    api_key=openai_api_key, 
    model="gpt-4o-mini"
)

llm_claude = ClaudeLLM(
    api_key=anthropic_api_key, 
    model="claude-3-5-sonnet-20240620"
)

# Generate responses
system_prompt = "Talk like a pirate. Keep answers short."
user_prompt = "What's the best reason to take a summer course in IoT?"

response_gpt = llm_gpt.generate(system_prompt, user_prompt)
response_claude = llm_claude.generate(system_prompt, user_prompt)

print(response_gpt)
print(response_claude)
```
Which outputs the following:

**gpt-4o-mini**
> Arrr, matey! A summer course in IoT be great fer learnin’ the ways o’ connected devices, boostin’ yer skills to hoist yer career sails! Ye’ll be ready to conquer new seas in tech! 🏴‍☠️⚓

**claude-3.5-sonnet**
> Arr, ye scurvy dog! The best reason be to learn how to make yer gadgets do yer biddin' from afar. It be like havin' a crew o' robots at yer command, savvy? Shiver me timbers, 'tis the future o' plunderin'!

##### :heavy_dollar_sign: API Costs and tokens
The API isn't free, and the price varies by model. An average adventure consists of ~20K Input tokens, 4K Output tokens which leads to the current price per adventure for today's (July 2025)



| Model            | $ / 1M Input | $ / 1M Output | $ / Adventure |
| ---------------- | ------------ | ------------- | ------------- |
| gpt-4.1          | 2            | 8             | 0.0720        |
| gpt-4.1-mini     | 0.4          | 1.6           | 0.0144        |
| gpt-4.1-nano     | 0.1          | 0.4           | 0.0036        |
| Claude Opus 4    | 15           | 75            | 0.6000        |
| Claude Sonnet 4  | 3            | 15            | 0.1200        |
| Claude Haiku 3.5 | 0.8          | 4             | 0.0320        |

The very best model is Claude Opus 4, but that's also reflected in the price. I picked Claude Haiku 3.5, since that was adequate, and cheap enough for me, but Sonnet 4 is quite the step up if your wallet can handle it.

Both OpenAI and Anthropic have *pay-as-you-go* plans which are great. You can deposit a minimum fee of 5$ which will last you quite a while. This also ensures that if a malicious actor gets access to your server and floods it with requests, it won't rack up huge bills.

#### SQLite
To store our sleep data, we will use a SQLite database using **sqlite3** from the Python standard library which makes it extremely easy to run SQL commands immediately from Python.
```python
connection = sqlite3.connect(self.db_path)
c.execute(
    "INSERT INTO statistics (type, value, timestamp) VALUES (?, ?, ?)",
    ("temperature", 24.7, "2025-06-30T11:00:00+02:00")
)
```

#### Dash
Finally Dash is used for our web dashboard which visualizes and plots our data. We track three key metrics: **sleep**, **bedtime**, and **wakeup**. Each metric is shown as both today's value, and a lineplot for historical data and trends.

The Dash app is written from scratch, by a combination of *HTML*, *CSS*, and Python w/ Plotly.
![image](https://hackmd.io/_uploads/S1mDA9cHxx.png)
> :lower_left_paintbrush: You can freely change the colors since they're defined as CSS variables in `server/assets/style.css`. They're used for both the site and the plots.

#### Comment on security, and connectivity design
We chose to use WiFi over other low-energy protocols like LoRa since power is not a constraint. I chose not to use any batteries, and instead use a 5V wall plug, since this alarm will be stationary at my nightstand. This makes the efficiency of low-power technologies irrelevant.

There is also no need for any large range, the alarm will only be used inside, near a bed, where one presumably has decent WiFi connection already.

#### Setup
Now let's set up the server. I'll assume you'll be doing this on the same computer on which you've already cloned the repo. If you wish to use another host as a server, simply clone the repo on it as you did before and follow these steps on that new host.

1. Enter the `server` directory, and install the required Python packages using `pip` in either a virtualenv, or your global Python isntallation
	```bash
	pip install -r requirements.txt
	```
    
2. Sign up and get your API keys from either [Anthropic](console.anthropic.com) (Claude) or [OpenAI](platform.openai.com).
    >:thinking_face: It's up to you whether to use OpenAI or Anthropic. In my testing, I found the OpenAI models to be more formulaic and way less interesting. The Claude models excel in coming up with interesting scenarios and choices but they're much more expensive.

3. Set these API keys as environment variables using by writing the following into a shell script `api_keys.sh`
    ```bash
    export OPENAI_API_KEY "YOUR_OPENAI_API_KEY"
    export ANTHROPIC_API_KEY "YOUR_ANTHROPIC_API_KEY"
    ```
    and running it using `source api_keys.sh`.
    
4. Start the server by running `python server.py`. In the `server` folder.
    > :warning: Make sure that you're in the correct folder when starting the server. Otherwise you may get **FileNotFoundError** when Dash searches for the CSS stylesheet in the `assets` folder.

## Running everything together
Now we're all done! To start the alarm, simply power it on with VS Code closed, or run `main.py` from VS Code. Make sure that
1. The server is **running**
2. The correct server IP-address is given in `main.py`
    ```python
    client = Client("http://<YOUR_SERVER_IP>:5000")
    ```
3. The WiFi SSID and password are stored in `client/wifi_settings.txt`.

## Final Results
### Alarm

[Watch on YouTube](https://youtu.be/WYNIS5jIoKA)
| Time  | Description                             |
| ----- | --------------------------------------- |
| 00:00 | Hand wave to show time                  |
| 00:13 | Setting the alarm                       |
| 00:34 | Waiting for the alarm to go off         |
| 01:31 | Alarm goes off!                         |
| 02:06 | Story beat 1                            |
| 02:42 | Choosing an action 1                    |
| 03:00 | Rolling dice 1                          |
| 03:18 | Story beat 2                            |
| 03:52 | Choosing an action and rolling dice 2   |
| 04:14 | Story beat 3                            |
| 04:44 | Choosing an action 3                    |
| 04:55 | Rolling dice 3                          |

### Dashboard
The final dashboard displays three key statistics
1. **Sleep** - how long you slept for
2. **Bedtime** - when you went to bed, counted from the last interaction with the alarm clock
3. **Wakeup** - when you got up, counted from when the alarm goes off.

At the very top you see the latest stats for today, below this you can see graphs and averages for the timeframe you specify in the dropdown menu.
![image](https://hackmd.io/_uploads/r1Pb6Vxrxx.png)

### Final Thoughts
This project has taught me a ton, but I wish to highlight three key lessons which I think everyone can learn from.

#### Physical buttons and dials are fun!
Tactile controls like buttons and knobs make interactions more engaging. Even simple interactions become meaningful if the buttons feel nice to use, and you get visual feedback. Rolling the dice in this alarm feels oddly thrilling and I think the tactile nature plays a key part.

#### LLMs and IoT are surprisingly easy to integrate
It's very easy to hook up IoT devices to LLMs with an intermediate server using the Python packages. I think there is a lot of unexplored territory here, from smart home assistant, voice controlled devices, or gamified and non-repetetive behaviour.

#### Fun is the easiest way to change behavior - Volkswagen’s "Fun Theory"
Adding playful elements (like gamified feedback) is much more motivating than a boring monotonous alarm sound. This drives lasting behavioral change far more effectively than rules or reminders. See Volkswagen's "Fun Theory".

## Thanks for reading!
If have any questions, don't hesitate to send an email to me at josefanhede1@gmail.com
