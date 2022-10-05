// Firebase configuration
console.log("----------------- ORDER PAGE ---------------------");
console.log(auth.TEST);
const firebaseConfig = {
    apiKey: auth.API_KEY,
    authDomain: auth.AUTH_DOMAIN,
    projectId: auth.PROJECT_ID,
    storageBucket: auth.STORAGE_BUCKET,
    messagingSenderId: auth.MESSAGING_SENDER_ID,
    appId: auth.APP_ID,
    measurementId: auth.MEASUREMENT_ID
};

firebase.initializeApp(firebaseConfig);
console.log("firebase success");
const firestore = firebase.firestore();
firestore.enablePersistence();

// **************** INDEX.html **************************
function addToFirestore(billItems, totalPrice, orderNum) {
    // const today = new Date()
    // const collectionName = "orders-" + today.getMonth() + "-" + today.getDate() + "-" + today.getFullYear();
    firestore.collection("orders").doc(orderNum.toString()).set({
        items: billItems,
        paidFor: true,
        totalPrice: totalPrice,
        timestamp: firebase.firestore.Timestamp.fromDate(new Date),
    })
    .then(() => {
        console.log("Document successfully written!");
    })
    .catch((error) => {
        console.error("Error writing document: ", error);
    });
}

// **************** ORDERS.html **************************
// Read previous orders from Firebase
var ordersList = document.getElementById("prev-orders-list");
firestore.collection("orders").get().then((querySnapshot) => {
    querySnapshot.forEach((doc) => {

        // For each order, print
        var orderNum = doc.id;
        var orderData = doc.data();

        console.log(`${doc.id} => ${doc.data()}`);
        console.log(Object.keys(doc.data()));
        console.log(doc.data().paidFor);
        console.log(typeof(orderData.items));
        console.log(orderData.items);

        // Order number
        var liOrderNum = document.createElement("li");
        liOrderNum.innerHTML = `<b>Order # ${orderNum}</b>`;

        // UL for each food item
        var ulFoodItems = document.createElement("ul");
        var liOrderDetails = document.createElement("li");
        liOrderDetails.innerHTML = `
            <li>Paid For: ${orderData.paidFor}</li>
            <li>Order Total Price: ${orderData.totalPrice}</li>
            <li>Order Timestamp: ${orderData.timestamp.toDate()}</li>
        `;
        ulFoodItems.style.listStyle = "none";
        ulFoodItems.appendChild(liOrderDetails);
        
        // Iterate through each food item in the order
        // Just returns the key. 
        for (const foodItem in orderData.items) {

            const foodItemDict = orderData.items[foodItem];
            console.log(foodItemDict["quantity"]);

            // Li for each food item
            var liFoodItem = document.createElement("li");
            liFoodItem.innerHTML = foodItem;
            
            // Ul for food details
            var ulFoodDetails = document.createElement("ul");
            ulFoodDetails.innerHTML =  `
                <li>Price Per Item: ${foodItemDict["pricePerItem"]}</li>
                <li>Quantity: ${foodItemDict["quantity"]}</li>
                <li>Item Total Price: ${foodItemDict["totalPrice"]}</li>
            `;

            // Append to Li foodItem
            liFoodItem.appendChild(ulFoodDetails);

            // Append food item to li
            ulFoodItems.appendChild(liFoodItem);
        }
        
        // Add details to each order
        liOrderNum.appendChild(ulFoodItems);
        
        // Add each order 
        ordersList.appendChild(liOrderNum);       

    });
});
