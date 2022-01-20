function addToCart(id, name, price, image) {
  event.preventDefault();

  // promise
  fetch("/api/add-to-cart", {
    method: "post",
    body: JSON.stringify({
      id: id,
      name: name,
      price: price,
      image: image,
    }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(function (res) {
      console.info(res);
      return res.json();
    })
    .then(function (data) {
      console.log(data);
      let d = document.getElementById("cartCounter");
      d.innerText = data.total_quantity;

      let cartCounter1 = document.getElementById("cartCounter1");
      cartCounter1.innerText = "";
      new Intl.NumberFormat().format(data.total_quantity) + " Items";

      let amount1 = document.getElementById("amount1");
      amount1.innerText =
        new Intl.NumberFormat().format(data.total_amount) + " VND";
    });
}

function pay() {
  if (confirm("Ban chac chan thanh toan khong?") == true) {
    fetch("/api/pay", {
      method: "post",
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        console.info(data);
        if (data.code == 200) location.reload();
      })
      .catch(function (err) {
        console.info(err);
      });
  }
}

function getValuePlus(name) {
  var value = document.getElementById(name).value;
  value++;
  console.log(value);
  return value;
}

function getValueMinus(name) {
  var value = document.getElementById(name).value;
  value--;
  console.log(value);
  return value;
}

function updateCartByInput(id, obj) {
  fetch("/api/update-cart", {
    method: "put",
    body: JSON.stringify({
      id: id,
      quantity: parseInt(obj.value),
    }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(function (res) {
      return res.json();
    })
    .then(function (data) {
      if (data.status === 200){
        let info = document.getElementsByClassName("cart-info");
        for (let i = 0; i < info.length; i++)
          info[i].innerText = data.data.total_quantity;

        let amount = document.getElementById("amountId");
        amount.innerText = new Intl.NumberFormat().format(data.data.total_amount);

        let amounts = document.getElementById("amountIds");
        amounts.innerText = new Intl.NumberFormat().format(data.data.total_amount);

        let cartCounter = document.getElementById("cartCounter");
        cartCounter.innerText = new Intl.NumberFormat().format(
          data.data.total_quantity
        );

        let cartCounter1 = document.getElementById("cartCounter1");
        cartCounter1.innerText =
          new Intl.NumberFormat().format(data.data.total_quantity) + " Items";

        let amount1 = document.getElementById("amount1");
        amount1.innerText =
          new Intl.NumberFormat().format(data.data.total_amount) + " VND";

        let p = document.getElementById("quantity" + id);
        p.innerText = new Intl.NumberFormat().format(parseInt(obj.value));
    }
    else{
      console.log(data)
      alert("Quantity in stock is not enough!!!")
      quantity = document.getElementById(data.data.id)
      quantity.value = data.data.quantity
      updateCartByButton(id=data.data.id, obj=data.data.quantity)
    }
  })
    .catch(function (err) {
      console.error(err);
    });
}

function updateCartByButton(id, obj) {
  fetch("/api/update-cart", {
    method: "put",
    body: JSON.stringify({
      id: id,
      quantity: obj,
    }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(function (res) {
      return res.json();
    })
    .then(function (data) {
      if (data.status === 200){
        console.log(data)

        let info = document.getElementsByClassName("cart-info");
        for (let i = 0; i < info.length; i++)
          info[i].innerText = data.data.total_quantity;

        let amount = document.getElementById("amountId");
        amount.innerText = new Intl.NumberFormat().format(data.data.total_amount);

        let amounts = document.getElementById("amountIds");
        amounts.innerText = new Intl.NumberFormat().format(data.data.total_amount);

        let cartCounter = document.getElementById("cartCounter");
        cartCounter.innerText = new Intl.NumberFormat().format(
          data.data.total_quantity
        );

        let cartCounter1 = document.getElementById("cartCounter1");
        cartCounter1.innerText =
          new Intl.NumberFormat().format(data.data.total_quantity) + " Items";

        let amount1 = document.getElementById("amount1");
        amount1.innerText =
          new Intl.NumberFormat().format(data.data.total_amount) + " VND";

        let p = document.getElementById("quantity" + id);
        p.innerText = new Intl.NumberFormat().format(obj);
      }
      else {
        console.log(data)
        alert("Quantity in stock is not enough")
        quantity = document.getElementById(data.data.id)
        quantity.value = data.data.quantity
        updateCartByInput(id=data.data.id, obj=data.data.quantity)

      }
    })
    .catch(function (err) {
    });
}

function deleteCart(bookId) {
  if (confirm("Are you sure?") == true) {
    fetch("/api/cart/" + bookId, {
      method: "delete",
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        let info = document.getElementsByClassName("cart-info");
        for (let i = 0; i < info.length; i++)
          info[i].innerText = data.total_quantity;

        let amount = document.getElementById("amountId");
        amount.innerText = new Intl.NumberFormat().format(data.total_amount);

        let amounts = document.getElementById("amountIds");
        amounts.innerText = new Intl.NumberFormat().format(data.total_amount);

        let cartCounter = document.getElementById("cartCounter");
        cartCounter.innerText = new Intl.NumberFormat().format(
          data.total_quantity
        );

        let cartCounter1 = document.getElementById("cartCounter1");
        cartCounter1.innerText =
          new Intl.NumberFormat().format(data.total_quantity) + " Items";

        let amount1 = document.getElementById("amount1");
        amount1.innerText =
          new Intl.NumberFormat().format(data.total_amount) + " VND";

        let p = document.getElementById("book" + bookId);
        p.style.display = "none";

        let p1 = document.getElementById("books" + bookId);
        p1.style.display = "none";
      })
      .catch(function (err) {
        location.reload();
      });
  }
}

function addComment(bookId) {
  let content = document.getElementById("commentContent");
  fetch("/api/comments", {
    method: "POST",
    body: JSON.stringify({
      content: content.value,
      book_id: bookId,
    }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      console.log(data);
      if (data.status === 200) {
        let comments = document.getElementById("comment");
        comments.innerHTML = getHtmlComments(data.data) + comments.innerHTML;
        content.value = "";

        let commentTitle = document.getElementById("comment-title");
        commentTitle.innerHTML = parseInt(commentTitle.innerHTML) + 1;
      } else alert("Them binh luan that bai");
    })
    .catch((err) => console.error(err));
}

let qttcomment = 0;

function loadComments(bookId) {
  qttcomment += 5;
  fetch(`/api/books/${bookId}/comments/${qttcomment}`)
    .then((res) => res.json())
    .then((data) => {
      console.info(data);
      let comments = document.getElementById("comment");
      comments.innerHTML = "";
      for (let i = 0; i < data.length; i++) {
        comments.innerHTML += getHtmlComments(data[i]);
      }
    });
}

function getHtmlComments(comment) {
  let image = comment.user.avatar;
  if (image === null || !image.startsWith("https"))
    image = "/static/img/avatar.png";

  return `
    <div class="single-comment">
        <img src="${image}" alt="${comment.user.username}" />
        <div class="content">
            <h4>${comment.user.username} <span>${moment(
    comment.created_date
  ).fromNow()}</span></h4>
            <p>${comment.content}</p>
            
        </div>
    </div>
    `;
}

function addActive() {
  var page = document.getElementsByClassName("pagination")[0].id;
  var page_li = document.getElementsByClassName("page-item");
  for (var i = 0; i < page_li.length; i++) {
    x = page_li[i].textContent;
    if (x == page) page_li[i].classList.add("active");
  }
}

function addActiveNav() {
  var url = window.location.pathname;
  var li = document.getElementsByClassName("activenav");
  for (var i = 0; i < li.length; i++) {
    x = li[i].id;
    if (x.includes(url)) li[i].classList.add("active");
  }
}

function miniCart(id, name, price, image) {
  fetch(`/api/add-to-cart/minicart`, {
    method: "post",
    body: JSON.stringify({
      id: id,
      name: name,
      price: price,
      image: image,
    }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((res) => res.json())
    .then((data) => {
      console.info(data);
      let comments = document.getElementById("shopping-list");
      comments.innerHTML = "";
      let result = [];
      for (var key in data) {
        result.push(data[key]);
        comments.innerHTML += getHtmlMiniCart(data[key]);
      }
      console.log(result);
    });
}

function getHtmlMiniCart(book) {
  return `
    <li id="books${book["id"]}">
        <a href="#" class="remove" title="Remove this item" onclick="deleteMiniCart(${
          book["id"]
        })"><i class="fa fa-remove"></i></a>
        <a class="cart-img" href="#"><img src="${book["image"]}" alt="${
    book["name"]
  }"></a>
        <h4><a href="#">${book.name}</a></h4>
        <p class="quantity" id="quantity${book.id}">${
    book.quantity
  } - <span class="amount">${new Intl.NumberFormat().format(
    book.price
  )}  VND</span></p>
    </li>
    `;
}

function deleteMiniCart(bookId) {
  fetch("/api/minicart/" + bookId, {
    method: "delete",
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(function (res) {
      return res.json();
    })
    .then(function (data) {
      let cartCounter = document.getElementById("cartCounter");
      cartCounter.innerText = new Intl.NumberFormat().format(
        data.total_quantity
      );

      let cartCounter1 = document.getElementById("cartCounter1");
      cartCounter1.innerText =
        new Intl.NumberFormat().format(data.total_quantity) + " Items";

      let amount1 = document.getElementById("amount1");
      amount1.innerText =
        new Intl.NumberFormat().format(data.total_amount) + " VND";

      let p = document.getElementById("books" + bookId);
      p.style.display = "none";
    })
    .catch(function (err) {
      console.error(err);
    });
}

function loadAddress(city_id) {
  fetch(`/api/load-address/${city_id}`)
    .then((res) => res.json())
    .then((data) => {
      $('#district').niceSelect('destroy');
      console.info(data);
      let comments = document.getElementById("district");
      comments.innerHTML = "";
      for (let i = 0; i < data.length; i++) {
        comments.innerHTML += getHtmlDistrict(data[i]);
        console.log(data[i]['name'])
      }
      $('#district').niceSelect();
    });
}

function getHtmlDistrict(district) {
  return `
  <option value=${district["id"]}>${district["name"]}</option>
    `;
}

function changeFunc() {
  var selectBox = document.getElementById('country');
  var selectedValue = selectBox.options[selectBox.selectedIndex].value;
  loadAddress(selectedValue); 
}

function toast({ title = "", message = "", type = "success", duration = 3000 }) {
  const main = document.getElementById("toast");
  if (main) {
    const toast = document.createElement("div");

    // Auto remove toast
    const autoRemoveId = setTimeout(function () {
      main.removeChild(toast);
    }, duration + 1000);

    // Remove toast when clicked
    toast.onclick = function (e) {
      if (e.target.closest(".toastclose")) {
        main.removeChild(toast);
        clearTimeout(autoRemoveId);
      }
    };
    const delay = (duration / 1000).toFixed(2);

    toast.classList.add("toast", `toast--${type}`);
    toast.style.animation = `slideInLeft ease .3s, fadeOut linear 1s ${delay}s forwards`;

    toast.innerHTML = `
                    <div class="toasticon">
                      <i class="fas fa-check-circle"></i>
                    </div>
                    <div class="toastbody">
                        <h3 class="toasttitle">${title}</h3>
                        <p class="toastmsg">${message}</p>
                    </div>
                    <div class="toastclose">
                        <i class="fas fa-times"></i>
                    </div>
                `;
    main.appendChild(toast);
  }
}

function showSuccessToast() {
  toast({
    title: "Add to cart",
    message: "Successfull",
    type: "success",
    duration: 1000
  });
}


function changeNotiRule(text = "", statics = "online"){
  const main = document.getElementById("NotiRule");
  // const types = document.getElementsByName("online");
  if(main){
    main.innerHTML = `<em>${text}</em>`
  }

  if(statics == "offline"){
    document.querySelectorAll('.online').forEach(function(el) {
      el.style.display = 'none';
   });
   $(".HideRequired").removeAttr('required');
  }

  if(statics == "online"){
    document.querySelectorAll('.online').forEach(function(el) {
      el.style.display = 'inline-block';
   });
   $(".HideRequired").attr('required', 'required');
  }
}

changeNotiRule(text = "", statics = "online")

function NotiRuleMOMO(){
  changeNotiRule(text = "", statics = "online")
}

function NotiRuleOffline(){
  changeNotiRule(text = "If you choose offline methods, you need to go to the book store to pay within 48 hours!!", statics = "offline")
}

$(document).ready(function(){
  $('.pass_show').append('<span class="ptxt" Style="width:40px;background-color:white;">Show</span>');
  });

  $(document).on('click','.pass_show .ptxt', function(){ 

  $(this).text($(this).text() == "Show" ? "Hide" : "Show"); 

  $(this).prev().attr('type', function(index, attr){return attr == 'password' ? 'text' : 'password'; }); 

  });