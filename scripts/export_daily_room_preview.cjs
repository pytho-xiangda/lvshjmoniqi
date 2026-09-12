/* Technical sprite registration and deterministic scene-animation export.
   Usage: node scripts/export_daily_room_preview.cjs [--video --ffmpeg PATH]
   Requires Playwright with a locally installed Edge browser. */
const fs=require('node:fs');
const path=require('node:path');
const http=require('node:http');
const {spawnSync}=require('node:child_process');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
const work=path.join(root,'.audio_runtime','daily-room-export');
const art=path.join(root,'assets','art','daily');
const args=process.argv.slice(2);
const ffmpeg=args.includes('--ffmpeg')?args[args.indexOf('--ffmpeg')+1]:'ffmpeg';
const png=data=>Buffer.from(data.split(',')[1],'base64');
fs.mkdirSync(work,{recursive:true});
const server=http.createServer((req,res)=>{
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  if(!pathname.startsWith('/docs/design/art/')&&!pathname.startsWith('/assets/art/daily/')){res.writeHead(403).end();return}
  const target=path.resolve(root,'.'+pathname);
  if(!target.startsWith(root+path.sep)||!fs.existsSync(target)||!fs.statSync(target).isFile()){res.writeHead(404).end();return}
  res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.png':'image/png'})[path.extname(target)]||'application/octet-stream');
  fs.createReadStream(target).pipe(res);
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const base=`http://127.0.0.1:${server.address().port}`;
  const browser=await chromium.launch({channel:'msedge',headless:true});
  const errors=[];
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1000}});
    page.on('pageerror',e=>errors.push(String(e)));
    await page.goto(base+'/docs/design/art/daily_room_preview.html?export&prepare');
    await page.evaluate(()=>window.roomReady);
    fs.writeFileSync(path.join(art,'characters','protagonist_walk_left_v01.png'),png(await page.evaluate(()=>window.roomDemo.atlas())));
    const metadata={columns:4,rows:2,frame_width:320,frame_height:480,frame_count:8,fps:8,foot_anchor:[160,460],direction:'left',alpha:'RGBA; connected-background matte and registration from generated RGB source',frames:Array.from({length:8},(_,i)=>({index:i,region:[(i%4)*320,Math.floor(i/4)*480,320,480]}))};
    fs.writeFileSync(path.join(art,'characters','protagonist_walk_left_v01.json'),JSON.stringify(metadata,null,2)+'\n');
    for(const [label,seconds] of [['door',0],['walking',4],['desk',8]]){
      await page.evaluate(t=>window.roomDemo.drawAt(t),seconds);
      fs.writeFileSync(path.join(work,label+'.png'),png(await page.evaluate(()=>window.roomDemo.snapshot())));
    }
    await page.evaluate(()=>window.roomDemo.drawAt(4));
    fs.writeFileSync(path.join(art,'daily_room_character_preview_v01.png'),png(await page.evaluate(()=>window.roomDemo.snapshot())));
    if(args.includes('--video')){
      const frames=136,fps=16;
      for(let i=0;i<frames;i++){
        await page.evaluate(t=>window.roomDemo.drawAt(t),i/fps);
        fs.writeFileSync(path.join(work,`frame_${String(i).padStart(4,'0')}.png`),png(await page.evaluate(()=>window.roomDemo.snapshot())));
      }
      const out=path.join(root,'assets','videos','daily_room_walk_v01.mp4');fs.mkdirSync(path.dirname(out),{recursive:true});
      const result=spawnSync(ffmpeg,['-hide_banner','-loglevel','error','-y','-framerate',String(fps),'-i',path.join(work,'frame_%04d.png'),'-vf','scale=1280:720:flags=lanczos','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart','-an',out],{windowsHide:true,encoding:'utf8'});
      if(result.error||result.status!==0)throw Error(result.error||result.stderr);
      console.log('Video exported: '+path.relative(root,out));
    }
    await page.goto(base+'/docs/design/art/daily_room_preview.html');await page.evaluate(()=>window.roomReady);
    await page.click('#computer');
    await page.waitForSelector('#panel:not([hidden])',{timeout:16000});
    if(await page.locator('#panel-title').innerText()!=='今天从哪件事开始？')throw Error('Computer interaction failed');
    await page.click('#close');await page.click('#computer');
    await page.waitForSelector('#panel:not([hidden])',{timeout:1000});
    if(!await page.evaluate(()=>{const p=window.roomDemo.position();return p.x===795&&p.y===795}))throw Error('Repeated desk click moved character');
    await page.click('#close');await page.click('#door');
    await page.waitForSelector('#panel:not([hidden])',{timeout:16000});
    if(await page.locator('#panel-title').innerText()!=='准备去哪里？')throw Error('Exit interaction failed');
    await page.keyboard.press('Escape');
    if(!await page.locator('#panel').evaluate(p=>p.hidden))throw Error('Escape failed');
    await page.click('#replay');
    await page.waitForFunction(()=>window.roomDemo.position().x<1250);
    const before=await page.evaluate(()=>window.roomDemo.position());
    await page.click('#computer');
    const after=await page.evaluate(()=>window.roomDemo.position());
    if(Math.hypot(before.x-after.x,before.y-after.y)>60)throw Error('Interrupting replay teleported character');
    await page.setViewportSize({width:390,height:844});
    if(!await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))throw Error('Mobile overflow');
    if(errors.length)throw Error(errors.join('\n'));
    const report={sprite_frames:8,frame_registration:[320,480],fps:8,computer_menu:true,repeated_desk_click:true,replay_interruption:true,exit_menu:true,escape:true,mobile_overflow:false,page_errors:errors};
    fs.writeFileSync(path.join(work,'validation.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
  }finally{await browser.close();server.close()}
})().catch(e=>{console.error(e);server.close();process.exitCode=1});
