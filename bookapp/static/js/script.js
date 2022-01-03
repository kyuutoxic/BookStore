function addToCart(id, name, price, image) {
    event.preventDefault()

    // promise
    fetch('/api/add-to-cart', {
        method: 'post',
        body: JSON.stringify({
            'id': id,
            'name': name,
            'price': price,
            'image': image
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res) {
        console.info(res)
        return res.json()
    }).then(function(data) {
        console.log(data)
        let d = document.getElementById('cartCounter')
        d.innerText = data.total_quantity

        let cartCounter1 = document.getElementById('cartCounter1')
        cartCounter1.innerText = new Intl.NumberFormat().format(data.total_quantity) + ' Items'

        let amount1 = document.getElementById('amount1')
        amount1.innerText = new Intl.NumberFormat().format(data.total_amount) +' VND'
    })
}

function pay() {
    if (confirm("Ban chac chan thanh toan khong?") == true) {
        fetch('/api/pay', {
            method: 'post'
        }).then(function(res) {
            return res.json()
        }).then(function(data) {
            console.info(data)
            if (data.code == 200)
                location.reload()
        }).catch(function(err) {
            console.info(err)
        })
    }

}

function getValuePlus(name){
    var value=document.getElementById(name).value;
    value++;  
    console.log(value)
    return value
}

function getValueMinus(name){
    var value=document.getElementById(name).value;
    value--;  
    console.log(value)
    return value
}

function updateCartByInput(id, obj) {
    fetch('/api/update-cart', {
         method: 'put',
         body: JSON.stringify({
             'id': id,
             'quantity': parseInt(obj.value)
         }),
         headers: {
             'Content-Type': 'application/json'
         }
     }).then(function(res) {
         return res.json()
     }).then(function(data) {
         let info = document.getElementsByClassName('cart-info')
         for (let i = 0; i < info.length; i++)
             info[i].innerText = data.total_quantity
 
         let amount = document.getElementById('amountId')
         amount.innerText = new Intl.NumberFormat().format(data.total_amount)

         let amounts = document.getElementById('amountIds')
         amounts.innerText = new Intl.NumberFormat().format(data.total_amount)

         let cartCounter = document.getElementById('cartCounter')
         cartCounter.innerText = new Intl.NumberFormat().format(data.total_quantity)

         let cartCounter1 = document.getElementById('cartCounter1')
         cartCounter1.innerText = new Intl.NumberFormat().format(data.total_quantity) + ' Items'

         let amount1 = document.getElementById('amount1')
         amount1.innerText = new Intl.NumberFormat().format(data.total_amount) +' VND'

         let p = document.getElementById('quantity' + id)
         p.innerText = new Intl.NumberFormat().format(parseInt(obj.value))


     }).catch(function(err) {
         console.error(err)
     })
 }

 function updateCartByButton(id, obj) {
    fetch('/api/update-cart', {
         method: 'put',
         body: JSON.stringify({
             'id': id,
             'quantity': obj
         }),
         headers: {
             'Content-Type': 'application/json'
         }
     }).then(function(res) {
         return res.json()
     }).then(function(data) {
         let info = document.getElementsByClassName('cart-info')
         for (let i = 0; i < info.length; i++)
             info[i].innerText = data.total_quantity
 
         let amount = document.getElementById('amountId')
         amount.innerText = new Intl.NumberFormat().format(data.total_amount)

         let amounts = document.getElementById('amountIds')
         amounts.innerText = new Intl.NumberFormat().format(data.total_amount)

         let cartCounter = document.getElementById('cartCounter')
         cartCounter.innerText = new Intl.NumberFormat().format(data.total_quantity)
         
         let cartCounter1 = document.getElementById('cartCounter1')
         cartCounter1.innerText = new Intl.NumberFormat().format(data.total_quantity) + ' Items'

         let amount1 = document.getElementById('amount1')
         amount1.innerText = new Intl.NumberFormat().format(data.total_amount) +' VND'

         let p = document.getElementById('quantity' + id)
         p.innerText = new Intl.NumberFormat().format(obj)


     }).catch(function(err) {
         console.error(err)
     })
 }

 function deleteCart(bookId) {
    if (confirm("Ban chac chan xoa mat hang khong?") == true) {
        fetch('/api/cart/' + bookId, {
            method: 'delete',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(function(res) {
            return res.json()
        }).then(function(data) {
            let info = document.getElementsByClassName('cart-info')
            for (let i = 0; i < info.length; i++)
                info[i].innerText = data.total_quantity

            let amount = document.getElementById('amountId')
            amount.innerText = new Intl.NumberFormat().format(data.total_amount)

            let amounts = document.getElementById('amountIds')
            amounts.innerText = new Intl.NumberFormat().format(data.total_amount)

            let cartCounter = document.getElementById('cartCounter')
            cartCounter.innerText = new Intl.NumberFormat().format(data.total_quantity)
         
            let cartCounter1 = document.getElementById('cartCounter1')
            cartCounter1.innerText = new Intl.NumberFormat().format(data.total_quantity) + ' Items'

            let amount1 = document.getElementById('amount1')
            amount1.innerText = new Intl.NumberFormat().format(data.total_amount) +' VND'


            let p = document.getElementById('book' + bookId)
            p.style.display = 'none'

            let p1 = document.getElementById('books' + bookId)
            p1.style.display = 'none'
        }).catch(function(err) {
            location.reload()
        })
    }

}

// function getHTMLCart() {

// }


// function loadCart(id) {
//     fetch('/api/add-to-cart'
//     ).then(function(res) {
//         console.info(res)
//         return res.json()
//     }).then(function(data) {
//         console.log(data)
//         cart = document.getElementById('viewcart')
//         cart.innerHTML = ""
//         for (let i = 0; i < data.length; i++)
//             cart.innerHTML += getHTMLCart(data[i])
//     })

// }