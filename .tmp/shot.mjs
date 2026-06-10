import { chromium } from 'playwright';
const url='https://retail-reactivation.vercel.app';
const b=await chromium.launch();
for (const [name,w,h] of [['desktop',1440,900],['mobile',375,812]]){
  const p=await b.newPage({viewport:{width:w,height:h}});
  await p.goto(url,{waitUntil:'networkidle'});
  await p.screenshot({path:`.tmp/taste-${name}.png`,fullPage:true});
  console.log(name,'shot ok');
  await p.close();
}
await b.close();
