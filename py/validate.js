re = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/

function validate_email(myform){
  // This script uses a regexp to check for a valid email address.
  // Address is optional
  if (myform.email.value==""){
    return true
  }

  if (re.test(myform.email.value)){
    return true
  }
  alert("Invalid email address")
  myform.email.focus()
  myform.email.select()
  return false
}

function validate_name(myform){
  // This script insists on a form field called name must have a value
  if (myform.name.value!=""){
    return true
  }

  alert("Please enter your name")
  myform.name.focus()
  myform.name.select()
  return false
}

