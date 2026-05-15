<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    if (!empty($_POST["choice"])) {
        $choice = htmlspecialchars($_POST["choice"]);
        echo "<h2>You selected: $choice</h2>";
    } else {
        echo "<h2>No option selected.</h2>";
    }
} else {
    echo "<h2>Invalid request.</h2>";
}
?>
