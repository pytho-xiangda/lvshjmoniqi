/* Fixed side-view renderer. The scene uses one horizontal ground line and a
   constant-size character so it maps directly to a 2D game coordinate system. */
const canvas=document.getElementById('room');
const ctx=canvas.getContext('2d');
const status=document.getElementById('status');
const panel=document.getElementById('panel');
const image=src=>new Promise((resolve,reject)=>{const value=new Image();value.onload=()=>resolve(value);value.onerror=reject;value.src=src});
const W=1672,H=941,GROUND_Y=795,DOOR_X=1360,DESK_X=650;
const FRAME_W=384,FRAME_H=530,CHARACTER_H=470,FOOT_Y=510,WALK_FPS=12,WALK_FRAME_COUNT=12;
let background,walkFrames=[],walkAtlas,idleFrame,playerX=DOOR_X,facingLeft=true,motion=null;
const exportMode=new URLSearchParams(location.search).has('export');

function removePaintedBackdrop(source){
  const work=document.createElement('canvas');work.width=source.width;work.height=source.height;
  const c=work.getContext('2d',{willReadFrequently:true});c.drawImage(source,0,0);
  const pixels=c.getImageData(0,0,work.width,work.height),data=pixels.data,count=work.width*work.height;
  const removed=new Uint8Array(count),queue=new Int32Array(count);let head=0,tail=0;
  function offer(p){if(p<0||p>=count||removed[p])return;const i=p*4,r=data[i],g=data[i+1],b=data[i+2];if(Math.max(r,g,b)-Math.min(r,g,b)>24||Math.min(r,g,b)<118)return;removed[p]=1;queue[tail++]=p}
  for(let x=0;x<work.width;x++){offer(x);offer((work.height-1)*work.width+x)}
  for(let y=0;y<work.height;y++){offer(y*work.width);offer(y*work.width+work.width-1)}
  while(head<tail){const p=queue[head++];if(p%work.width)offer(p-1);if(p%work.width<work.width-1)offer(p+1);offer(p-work.width);offer(p+work.width)}
  for(let p=0;p<count;p++)if(removed[p])data[p*4+3]=0;
  const seen=new Uint8Array(count);let largest=[];
  for(let p=0;p<count;p++){
    if(seen[p]||!data[p*4+3])continue;head=0;tail=0;queue[tail++]=p;seen[p]=1;
    while(head<tail){const a=queue[head++];for(const b of [a%work.width?a-1:-1,a%work.width<work.width-1?a+1:-1,a-work.width,a+work.width])if(b>=0&&b<count&&!seen[b]&&data[b*4+3]){seen[b]=1;queue[tail++]=b}}
    if(tail>largest.length)largest=Array.from(queue.subarray(0,tail));
  }
  const keep=new Uint8Array(count);for(const p of largest)keep[p]=1;
  let left=work.width,right=0,top=work.height,bottom=0;
  for(let p=0;p<count;p++){if(!keep[p]){data[p*4+3]=0;continue}const x=p%work.width,y=Math.floor(p/work.width);left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y)}
  c.putImageData(pixels,0,0);return{canvas:work,left,right,top,bottom};
}

function normalize(source){
  const cut=removePaintedBackdrop(source),out=document.createElement('canvas');out.width=FRAME_W;out.height=FRAME_H;
  const scale=CHARACTER_H/(cut.bottom-cut.top+1);
  let waistSum=0,waistCount=0;const c=cut.canvas.getContext('2d',{willReadFrequently:true});
  const pixels=c.getImageData(0,0,cut.canvas.width,cut.canvas.height).data;
  for(let y=Math.round(cut.top+(cut.bottom-cut.top)*.39);y<cut.top+(cut.bottom-cut.top)*.49;y++)for(let x=cut.left;x<=cut.right;x++)if(pixels[(y*cut.canvas.width+x)*4+3]){waistSum+=x;waistCount++}
  const anchorX=waistCount?waistSum/waistCount:(cut.left+cut.right)/2;
  out.getContext('2d').drawImage(cut.canvas,FRAME_W/2-anchorX*scale,FOOT_Y-cut.bottom*scale,cut.canvas.width*scale,cut.canvas.height*scale);
  return out;
}

function buildAtlas(sources){
  walkFrames=sources.map(normalize);walkAtlas=document.createElement('canvas');walkAtlas.width=FRAME_W*4;walkAtlas.height=FRAME_H;
  const c=walkAtlas.getContext('2d');walkFrames.forEach((frame,index)=>c.drawImage(frame,index*FRAME_W,0));
  return walkAtlas;
}

function drawAmbient(seconds){
  ctx.save();ctx.globalCompositeOperation='screen';ctx.fillStyle='#f6d9a512';
  const drift=Math.sin(seconds*.55)*9;
  for(const [x,y,rx,ry] of [[165,778,58,13],[300,825,74,15],[455,765,52,11],[565,838,67,13]]){ctx.beginPath();ctx.ellipse(x+drift,y,rx,ry,-.18,0,Math.PI*2);ctx.fill()}
  ctx.globalCompositeOperation='source-over';
  for(let index=0;index<14;index++){const x=125+(index*79)%500+Math.sin(seconds*.42+index)*7,y=125+(index*113)%500+Math.cos(seconds*.31+index)*5;ctx.fillStyle=`rgba(255,244,211,${.06+(index%4)*.025})`;ctx.beginPath();ctx.arc(x,y,1+(index%3)*.45,0,Math.PI*2);ctx.fill()}
  ctx.restore();
}

function draw(x=playerX,frame=0,moving=false,left=facingLeft,seconds=0){
  ctx.clearRect(0,0,W,H);ctx.drawImage(background,0,0,W,H);drawAmbient(seconds);
  const bob=moving?[0,1,2,1,0,-1,0,1,2,1,0,-1][frame%WALK_FRAME_COUNT]:0;
  ctx.save();ctx.translate(x,GROUND_Y-bob);ctx.fillStyle='#241b1829';ctx.filter='blur(4px)';ctx.beginPath();ctx.ellipse(0,bob-3,43,9,0,0,Math.PI*2);ctx.fill();ctx.filter='none';
  ctx.scale(left?1:-1,1);const sprite=moving?walkFrames[frame]:idleFrame;ctx.drawImage(sprite,-FRAME_W/2,-FOOT_Y);ctx.restore();
}

function demoAt(seconds){
  const progress=Math.max(0,Math.min(1,(seconds-.5)/5));
  const moving=seconds>=.5&&seconds<5.5;const x=DOOR_X+(DESK_X-DOOR_X)*progress;
  draw(x,moving?Math.floor((seconds-.5)*WALK_FPS)%WALK_FRAME_COUNT:0,moving,true,seconds);return{x,progress,moving};
}

function moveTo(targetX,open=null){
  panel.hidden=true;targetX=Math.max(560,Math.min(1420,targetX));
  if(Math.abs(playerX-targetX)<1){if(open)showPanel(open);return}
  facingLeft=targetX<playerX;motion={from:playerX,to:targetX,start:performance.now(),duration:Math.max(350,Math.abs(targetX-playerX)/140*1000),open};status.textContent=facingLeft?'向左行走…':'向右行走…';
}

function showPanel(kind){
  panel.hidden=false;document.getElementById('feedback').textContent='';
  document.getElementById('panel-kicker').textContent=kind==='desk'?'工作电脑':'外出';
  document.getElementById('panel-title').textContent=kind==='desk'?'今天从哪件事开始？':'准备去哪里？';
  document.getElementById('panel-desc').textContent=kind==='desk'?'选择一项办公行动。':'正式游戏按章节显示已解锁目的地。';
  const options=document.getElementById('options');options.replaceChildren();
  for(const label of kind==='desk'?['整理卷宗','检索法条','查看来信','返回房间']:['律所公共区','法院','街区','留在房间']){
    const button=document.createElement('button');button.textContent=label;button.onclick=()=>{if(label==='返回房间'||label==='留在房间'){panel.hidden=true;return}document.getElementById('feedback').textContent=`已选择「${label}」。此处为游戏交互原型，尚未接入正式任务。`};options.append(button);
  }
}

function animate(now){
  if(!exportMode){
    if(motion?.demo){const seconds=(now-motion.start)/1000;const state=demoAt(seconds);playerX=state.x;facingLeft=true;if(seconds>=6){playerX=DESK_X;motion=null;draw(playerX,0,false,facingLeft,now/1000);status.textContent='已到电脑桌前。'}}
    else if(motion){const p=Math.min(1,(now-motion.start)/motion.duration);playerX=motion.from+(motion.to-motion.from)*p;draw(playerX,Math.floor((now-motion.start)/1000*WALK_FPS)%WALK_FRAME_COUNT,p<1,facingLeft,now/1000);if(p===1){const open=motion.open;motion=null;draw(playerX,0,false,facingLeft,now/1000);status.textContent='已到达。';if(open)showPanel(open)}}
    else draw(playerX,0,false,facingLeft,now/1000);
  }
  requestAnimationFrame(animate);
}

document.getElementById('replay').onclick=()=>{panel.hidden=true;playerX=DOOR_X;facingLeft=true;motion={demo:true,start:performance.now()};status.textContent='门口 → 电脑桌';};
for(const id of ['computer','desk-hotspot'])document.getElementById(id).onclick=()=>moveTo(DESK_X,'desk');
for(const id of ['door','exit-hotspot'])document.getElementById(id).onclick=()=>moveTo(DOOR_X,'door');
document.getElementById('close').onclick=()=>{panel.hidden=true};
window.addEventListener('keydown',event=>{if(event.key==='Escape')panel.hidden=true});
canvas.addEventListener('click',event=>{const rect=canvas.getBoundingClientRect(),x=(event.clientX-rect.left)/rect.width*W,y=(event.clientY-rect.top)/rect.height*H;if(y>705)moveTo(x)});

const base='../../../assets/art/daily/characters/';
window.roomReady=Promise.all([image('../../../assets/art/daily/daily_room_side_v04.png'),image(base+'protagonist_side_walk_v04.png'),image(base+'protagonist_side_idle_v04.png')]).then(values=>{
  background=values[0];
  walkAtlas=values[1];for(let index=0;index<WALK_FRAME_COUNT;index++){const frame=document.createElement('canvas');frame.width=FRAME_W;frame.height=FRAME_H;frame.getContext('2d').drawImage(walkAtlas,(index%6)*FRAME_W,Math.floor(index/6)*FRAME_H,FRAME_W,FRAME_H,0,0,FRAME_W,FRAME_H);walkFrames.push(frame)}idleFrame=values[2];
  draw();status.textContent='点击地板移动，或选择办公、外出。';
  window.sideRoomDemo={drawAt:demoAt,walkAtlas:()=>walkAtlas.toDataURL('image/png'),idle:()=>idleFrame.toDataURL('image/png'),snapshot:()=>canvas.toDataURL('image/png'),position:()=>({x:playerX,y:GROUND_Y}),moveTo};
  requestAnimationFrame(animate);return true;
}).catch(error=>{status.textContent='素材载入失败，请通过本地预览服务器打开。';throw error});
