function increment(txt_name)
{
   qty = document.getElementById(txt_name);
   num = parseInt(qty.value);
   if (num<7)
    {
       num +=1;
       qty.value = num;
   }
  }

function decrement(txt_name)
{
   qty = document.getElementById(txt_name);
   num = parseInt(qty.value);
   if (num>1)
   {
       num -=1;
       qty.value = num;
   }
  
  }
