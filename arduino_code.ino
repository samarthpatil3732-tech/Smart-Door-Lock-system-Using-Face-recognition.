
// use the arduino Uno to run this code

#define LED_PIN 13   // LED indicates door status 
#define LOCK_PIN 12  // Lock control pin 
bool isUnlocked = false; // Track door state 
void setup() { 
DDRB |= (1 << DDB5); // Pin 13 as OUTPUT 
DDRB |= (1 << DDB4); // Pin 12 as OUTPUT 
// Initially lock the door 
PORTB &= ~(1 << PORTB4); // Lock LOW 
PORTB &= ~(1 << PORTB5); // LED OFF 
Serial.begin(9600); 
Serial.println("Arduino Ready"); 
} 
void loop() { 
if (Serial.available() > 0) { 
String command = Serial.readStringUntil('\n'); 
command.trim(); 
if (!isUnlocked && command == "U") { 
// Unlock door 
      PORTB |= (1 << PORTB4);  // Unlock pin HIGH 
      PORTB |= (1 << PORTB5);  // LED ON 
      isUnlocked = true;       // Update status 
      Serial.println("Door Unlocked"); 
 
    } else if (isUnlocked && command == "L") { 
      // Lock door 
      PORTB &= ~(1 << PORTB4); // Lock pin LOW 
      PORTB &= ~(1 << PORTB5); // LED OFF 
      isUnlocked = false;      // Update status 
      Serial.println("Door Locked"); 
 
    } else { 
      Serial.println("Command Ignored"); 
    } 
  } 
}
