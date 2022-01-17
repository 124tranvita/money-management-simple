"use strict";

/* Định dạng lại số tiền nhập vào (theo format 1,000,000) cho các ô nhập tiền vào khoản chi */
const moneyInput = document.querySelector("#moneyInput");

/* Hiển thị số tiền trong tag input theo $ format */
const currentValue = Number(moneyInput.value);
moneyInput.value = currentValue.toLocaleString();
console.log(currentValue);

moneyInput.addEventListener("keyup", function () {
  let value = parseInt(this.value.replace(/\D/g, ""), 10);
  if (isNaN(value)) {
    return;
  }
  this.value = value.toLocaleString();
});

/* Vì giá trị trả về của toLocaleString là string, nên khi submit khoản chi, cần chuyển số tiền từ String trở lại Number*/
const submit = document.querySelector("#submit");

submit.addEventListener("click", function () {
  /* Chuyển số tiền nhập (đã được format) từ string về lại number (thay các dấu , = '') */
  let value = parseInt(moneyInput.value.replace(/\D/g, ""), 10);
  if (isNaN(value)) {
    return;
  }
  moneyInput.value = value;
});
