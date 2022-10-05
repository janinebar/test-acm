var orderNum = 1;

const foods = ["Hamburger", "Cheeseburger", "Hotdog", "Fries"];
const drinks = ["Coke", "Pepsi", "Dr. Pepper", "Juice"];
const snacks = ["Cookie", "Ice Cream", "Brownie", "Candy"];
const condiments = ["Ketchup", "Mustard", "Mayonnaise", "Ranch"];
var prices = {
    "foods": 5,
    "drinks": 2.5,
    "snacks": 3,
    "condiments": 0.5,
}
var totalPrice = 0;

function addToBill(itemName) {
    // Find a <table> element with id="bill":
    var table = document.getElementById("bill-table");

    // Create an empty <tr> element and add it to the end position of the table:
    var row = table.insertRow();

    // Insert new cells (<td> elements) at the 1st and 2nd position of the "new" <tr> element:
    var item = row.insertCell();
    var price = row.insertCell();

    // Add item and price to bill:
    item.innerHTML = itemName;
    var itemPrice = getItemPrice(itemName);
    price.innerHTML = "$" + formatPrice(itemPrice);

    item.style.width = "70%";
    price.style.width = "30%";

    addTotal(itemPrice);
}

function addTotal(itemPrice) {
    // Get <td> holding total price
    totalPrice += itemPrice;
    document.getElementById("bill-total-td").innerHTML = "$" + formatPrice(totalPrice);
} 

function togglePaymentLightbox() {
    var lightboxWrapper = document.getElementById("lightbox-wrapper");
    var lightbox = document.getElementById("lightbox");

    if (lightboxWrapper.style.display == "none" && lightbox.style.display == "none") {
        lightboxWrapper.style.display = "block";
        lightbox.style.display = "block";
    } else {
        lightboxWrapper.style.display = "none";
        lightbox.style.display = "none";
    }

    // Animate payment processing
    var lightboxText = document.getElementById("lightbox-p");
    lightboxText.innerHTML = "Payment processing...";

    // Turn current bill to map to save to firestore
    const billItems = billToMap();

    // Save to firestore
    addToFirestore(billItems, totalPrice, orderNum);
            
    // clearTimeout(timeout);
    // timeout = setTimeout(function() {
        lightboxText.innerHTML = "Payment successful!";
    // }, 2000);
    timeout = setTimeout(function() {
        lightboxWrapper.style.display = "none";
    lightbox.style.display = "none";
    }, 4000);

    newOrder();

}

function toggleReceiptLightbox() {
    var lightboxWrapper = document.getElementById("lightbox-wrapper");
    var lightbox = document.getElementById("lightbox");

    if (lightboxWrapper.style.display == "none" && lightbox.style.display == "none") {
        lightboxWrapper.style.display = "block";
        lightbox.style.display = "block";
    } else {
        lightboxWrapper.style.display = "none";
        lightbox.style.display = "none";
    }
    
    // Animate print receipt
    var lightboxText = document.getElementById("lightbox-p");
    lightboxText.innerHTML = "Printing receipt...";
    timeout = setTimeout(function() {
        lightboxWrapper.style.display = "none";
    lightbox.style.display = "none";
    }, 4000);
}

function clearBill() {
    var billTable = document.getElementById("bill-table");
    var numRows = billTable.rows.length;
    for (let row = numRows-1; row > 0; row--){
        console.log(row);
        billTable.deleteRow(row);
        console.log(numRows);
    }

    // Reset bill total
    totalPrice = 0;
    document.getElementById("bill-total-td").innerHTML = "";

}

function updateOrder() {
    orderNum++;
    document.getElementById("order-num-p").innerHTML = "Order #" + orderNum;
}

function newOrder() {
    clearBill();
    updateOrder();

}

var currentBillItemIndex = 0;

function selectBillItem(direction) {

    var billTable = document.getElementById("bill-table");
    var numRows = billTable.rows.length;

    // Choose correct item
    if (direction == "down" && currentBillItemIndex < numRows-1){ 
        currentBillItemIndex++;
        prevBillItemIndex = currentBillItemIndex-1;
    }
    else if (direction == "up" && currentBillItemIndex > 1){
        currentBillItemIndex--;
        prevBillItemIndex = currentBillItemIndex+1;
    }
    
    console.log("currentRow: " + currentBillItemIndex);
    console.log("prevRow: " + prevBillItemIndex);

    // Highlight selected row
    var itemRow = document.getElementById("bill-table").rows[currentBillItemIndex];
    itemRow.style.backgroundColor = "black";
    itemRow.style.color = "white";
    
    // Unhighlight previously selected row 
    var prevItemRow = document.getElementById("bill-table").rows[prevBillItemIndex];
    prevItemRow.style.backgroundColor = "white";
    prevItemRow.style.color = "black";

}

function restartSelection() {
    // Get currently selected item
    var itemRow = document.getElementById("bill-table").rows[currentBillItemIndex];

    // Unhiglight current item
    itemRow.style.backgroundColor = "white";
    itemRow.style.color = "black";

    // reset currentBillItemIndex
    currentBillItemIndex = 0;
}

function removeBillItem() {

    if (currentBillItemIndex > 0){
        // Get item name
        var itemRow = document.getElementById("bill-table").rows[currentBillItemIndex];
        console.log("item: " + itemRow.cells[0].innerText);
        var itemName = itemRow.cells[0].innerText;

        // Find item price
        var itemPrice = getItemPrice(itemName);

        // update total
        totalPrice -= itemPrice;
        document.getElementById("bill-total-td").innerHTML = "$" + formatPrice(totalPrice);
        
        // delete row from UI
        document.getElementById("bill-table").deleteRow(currentBillItemIndex);

        // reset currentBillItemIndex
        currentBillItemIndex = 0;
    }
}

function getItemPrice(itemName) {
    var itemPrice = 0;
    if (foods.includes(itemName)){ 
        return itemPrice = prices["foods"];
    }
    else if (drinks.includes(itemName)) {
        return itemPrice = prices["drinks"];
    }
    else if (snacks.includes(itemName)) {
        return itemPrice = prices["snacks"];
    }
    else if (condiments.includes(itemName)) {
        return itemPrice = prices["condiments"];
    }

    return itemPrice;
}

function formatPrice(price) {
    return price % 1 == 0 ? price.toString() + ".00" : price.toString() + "0" ;
}

// Convert bill items to map
function billToMap() {
    var billTable = document.getElementById("bill-table");
    var billItems = {};

    console.log("billtomap");
    //Iterate through bill items
    for(i = 1; i < billTable.rows.length; i++){
        var itemName = billTable.rows[i].cells[0].innerText;
        var itemPrice = getItemPrice(itemName);
        console.log(itemName);
        console.log(itemPrice);

        // If already in dict, just update quantity
        if (billItems.hasOwnProperty(itemName)){
            console.log("in dict");
            const item = billItems[itemName];
            item.quantity += 1;
            item.totalPrice = item.quantity * item.pricePerItem;
        }
        // Else add to dict
        else {
            billItems[itemName] = {
                "pricePerItem": itemPrice,
                "quantity": 1,
                "totalPrice": itemPrice
            }
        }
    }
    console.log(JSON.stringify(billItems));
    return billItems;
}