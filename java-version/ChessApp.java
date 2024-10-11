import javax.swing.*;
import java.awt.*;

public class ChessApp {
    public static void main(String[] args) {
        JFrame frame = new JFrame("Chess Game");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(500, 500);
        frame.setLayout(new GridLayout(8, 8));

        // Create an 8x8 grid
        for (int row = 0; row < 8; row++) {
            for (int col = 0; col < 8; col++) {
                JPanel panel = new JPanel();
                panel.setPreferredSize(new Dimension(60, 60));

                // Alternate colors
                if ((row + col) % 2 == 0) {
                    panel.setBackground(Color.WHITE);
                } else {
                    panel.setBackground(Color.BLACK);
                }

                frame.add(panel);
            }
        }

        frame.setVisible(true);
    }
}
