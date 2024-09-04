import java.util.Random;
import java.util.Scanner;

public class Task_1_Number_Game {

    public static void main(String[] args) {
        Scanner userInputScanner = new Scanner(System.in);
        Random randomNumberGenerator = new Random();
        
        int minimumNumberRange = 1;
        int maximumNumberRange = 100;
        int maximumGuessAttempts = 7;
        int totalScore = 0;
        
        System.out.println("Welcome to the Number Guessing Game!\n");
        boolean continuePlaying = true;
        
        while (continuePlaying) {
            int secretNumber = randomNumberGenerator.nextInt(maximumNumberRange - minimumNumberRange + 1) + minimumNumberRange;
            System.out.printf("Round - Range: %d to %d\n", minimumNumberRange, maximumNumberRange);
            System.out.println("You have " + maximumGuessAttempts + " attempts.\n");
            
            int numberOfAttempts = 0;
            boolean guessedCorrectlyFlag = false;
            
            while (numberOfAttempts < maximumGuessAttempts) {
                System.out.print("Enter your guess: ");
                int userGuessedNumber = userInputScanner.nextInt();
                
                numberOfAttempts++;
                
                if (userGuessedNumber == secretNumber) {
                    System.out.printf("Correct! You guessed the number in %d attempts.\n", numberOfAttempts);
                    totalScore += numberOfAttempts;
                    guessedCorrectlyFlag = true;
                    break;
                } else if (userGuessedNumber < secretNumber) {
                    System.out.println("Too low! Try again.\n");
                } else {
                    System.out.println("Too high! Try again.\n");
                }
            }
            
            if (!guessedCorrectlyFlag) {
                System.out.println("Sorry, you've used all your attempts. The correct number was " + secretNumber);
            }
            
            System.out.println("Your current score: " + totalScore + "\n");
            
            System.out.print("Do you want to play another round? (yes/no): ");
            String playAgainResponse = userInputScanner.next().toLowerCase();
            if (!playAgainResponse.equals("yes")) {
                continuePlaying = false;
            }
        }
        
        System.out.println("Thank you for playing! Your final score: " + totalScore);
        
        userInputScanner.close();
    }
}
