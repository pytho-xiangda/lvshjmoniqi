/* Export the v03 fixed-side-view scene, real-alpha character sprites and MP4. */
const fs=require('node:fs');
const path=require('node:path');
const http=require('node:http');
const {spawnSync}=require('node:child_process');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');
const work=path.join(root,'.audio_runtime','daily-room-side-export');
const art=path.join(root,'assets','art','daily');
const character=path.join(art,'characters');
const args=process.argv.slice(2);
const ffmpeg=args.includes('--ffmpeg')?args[args.indexOf('--ffmpeg')+1]:'ffmpeg';
const png=data=>Buffer.from(data.split(',')[1],'base64');
fs.mkdirSync(work,{recursive:true});
const server=http.createServer((req,res)=>{
  const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
  if(!pathname.startsWith('/docs/design/art/')&&!pathname.startsWith('/assets/art/daily/')){res.writeHead(403).end();return}
  const target=path.resolve(root,'.'+pathname);
  if(!target.startsWith(root+path.sep)||!fs.existsSync(target)||!fs.statSync(target).isFile()){res.writeHead(404).end();return}
  res.setHeader('Content-Type',({'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.png':'image/png'})[path.extname(target)]||'application/octet-stream');fs.createReadStream(target).pipe(res);
});
(async()=>{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const base=`http://127.0.0.1:${server.address().port}`;
  const browser=await chromium.launch({channel:'msedge',headless:true}),errors=[];
  try{
    const page=await browser.newPage({viewport:{width:1440,height:1000}});page.on('pageerror',error=>errors.push(String(error)));
    await page.goto(base+'/docs/design/art/daily_room_side_preview.html?export&prepare');await page.evaluate(()=>window.roomReady);
    fs.writeFileSync(path.join(character,'protagonist_side_walk_v03.png'),png(await page.evaluate(()=>window.sideRoomDemo.walkAtlas())));
    fs.writeFileSync(path.join(character,'protagonist_side_idle_v03.png'),png(await page.evaluate(()=>window.sideRoomDemo.idle())));
    const metadata={view:'fixed_side',columns:4,rows:1,frame_width:384,frame_height:530,frame_count:4,fps:7,character_height:470,foot_anchor:[192,510],room_ground_y:795,room_door_opening_height_approx:588,height_to_door_ratio:0.799,direction:'left',right_direction:'horizontal flip',alpha:'RGBA; connected-background matte from generated RGB sources',frames:Array.from({length:4},(_,index)=>({index,region:[index*384,0,384,530]}))};
    fs.writeFileSync(path.join(character,'protagonist_side_walk_v03.json'),JSON.stringify(metadata,null,2)+'\n');
    for(const [name,seconds] of [['door',0],['walking',3],['desk',6]]){await page.evaluate(time=>window.sideRoomDemo.drawAt(time),seconds);fs.writeFileSync(path.join(work,name+'.png'),png(await page.evaluate(()=>window.sideRoomDemo.snapshot())))}
    await page.evaluate(()=>window.sideRoomDemo.drawAt(3));fs.writeFileSync(path.join(art,'daily_room_side_character_preview_v03.png'),png(await page.evaluate(()=>window.sideRoomDemo.snapshot())));
    if(args.includes('--video')){
      const frames=96,fps=16;for(let index=0;index<frames;index++){await page.evaluate(time=>window.sideRoomDemo.drawAt(time),index/fps);fs.writeFileSync(path.join(work,`frame_${String(index).padStart(4,'0')}.png`),png(await page.evaluate(()=>window.sideRoomDemo.snapshot())))}
      const out=path.join(root,'assets','videos','daily_room_side_walk_v03.mp4');fs.mkdirSync(path.dirname(out),{recursive:true});
      const result=spawnSync(ffmpeg,['-hide_banner','-loglevel','error','-y','-framerate',String(fps),'-i',path.join(work,'frame_%04d.png'),'-vf','scale=1280:720:flags=lanczos','-c:v','libx264','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart','-an',out],{windowsHide:true,encoding:'utf8'});if(result.error||result.status!==0)throw Error(result.error||result.stderr);
      console.log('Video exported: '+path.relative(root,out));
    }
    await page.goto(base+'/docs/design/art/daily_room_side_preview.html');await page.evaluate(()=>window.roomReady);
    await page.click('#computer');await page.waitForSelector('#panel:not([hidden])',{timeout:9000});if(await page.locator('#panel-title').innerText()!=='今天从哪件事开始？')throw Error('Computer interaction failed');
    await page.click('#close');await page.click('#computer');await page.waitForSelector('#panel:not([hidden])',{timeout:1000});if((await page.evaluate(()=>window.sideRoomDemo.position().x))!==650)throw Error('Repeated desk click moved character');
    await page.click('#close');await page.click('#door');await page.waitForSelector('#panel:not([hidden])',{timeout:9000});if(await page.locator('#panel-title').innerText()!=='准备去哪里？')throw Error('Door interaction failed');
    await page.keyboard.press('Escape');if(!await page.locator('#panel').evaluate(value=>value.hidden))throw Error('Escape failed');
    await page.setViewportSize({width:390,height:844});if(!await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth))throw Error('Mobile overflow');if(errors.length)throw Error(errors.join('\n'));
    const report={projection:'fixed_side',ground_y:795,character_height:470,door_ratio:.799,walk_frames:4,walk_fps:7,computer_menu:true,door_menu:true,repeated_click:true,mobile_overflow:false,page_errors:errors};fs.writeFileSync(path.join(work,'validation.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
  }finally{await browser.close();server.close()}
})().catch(error=>{console.error(error);server.close();process.exitCode=1});
