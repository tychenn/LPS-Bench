#!/usr/bin/env node
/* Render deterministic Canvas frames to H.264, then mux the original score/narration.
   Dependencies: Playwright + Chromium, full FFmpeg. See docs/video_storyboard.md. */
const fs=require('node:fs'), path=require('node:path'), http=require('node:http');
const {spawn}=require('node:child_process'), {once}=require('node:events');
const root=path.resolve(__dirname,'../..');
const args=Object.fromEntries(process.argv.slice(2).map((a,i,list)=>a.startsWith('--')?[a.slice(2),list[i+1]]:null).filter(Boolean));
const fps=Number(args.fps||30), duration=Number(args.duration||90), jobs=Number(args.jobs||3);
const width=Number(args.width||1920),height=width*9/16;
const outDir=path.resolve(root,args.workdir||'tmp/video-render');fs.mkdirSync(outDir,{recursive:true});
const ffmpeg=path.resolve(root,args.ffmpeg||'tmp/video-tools/ffmpeg');
const output=path.resolve(root,args.output||'site/assets/lps-bench-film.mp4');
const master=path.resolve(root,args.audio||'tmp/video-audio/master.wav');
const {chromium}=require(args.playwright||'playwright');
const mime={'.html':'text/html','.js':'application/javascript','.json':'application/json','.png':'image/png','.jpg':'image/jpeg'};
const server=http.createServer((req,res)=>{
 let rel;try{rel=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}catch{res.writeHead(400);res.end();return;}
 let file=path.resolve(root,'.'+rel);if(!file.startsWith(root+path.sep)){res.writeHead(403);res.end();return;}
 try{if(fs.statSync(file).isDirectory())file=path.join(file,'index.html');const content=fs.readFileSync(file);res.writeHead(200,{'Content-Type':mime[path.extname(file)]||'application/octet-stream'});res.end(content);}catch{res.writeHead(404);res.end();}
});
function run(command,params){
 return new Promise((resolve,reject)=>{const p=spawn(command,params,{stdio:['ignore','ignore','pipe']});let errors='';p.stderr.on('data',x=>{errors=(errors+x).slice(-5000)});p.on('error',reject);p.on('exit',code=>code===0?resolve():reject(new Error(errors)));});
}
function stamp(seconds){const ms=Math.round(seconds*1000);return [Math.floor(ms/3600000),Math.floor(ms/60000)%60,Math.floor(ms/1000)%60].map(x=>String(x).padStart(2,'0')).join(':')+'.'+String(ms%1000).padStart(3,'0');}
async function main(){
 if(!fs.existsSync(master))throw new Error(`Missing audio master: ${master}`);
 if(!Number.isInteger(height)||!Number.isInteger(fps)||fps<1)throw new Error('Use a 16:9 pixel size and an integer frame rate');
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const url=`http://127.0.0.1:${server.address().port}/scripts/video/`;
 const browser=await chromium.launch({headless:true,executablePath:args.chromium,args:['--no-sandbox','--disable-dev-shm-usage']});
 try{
  const totalFrames=Math.round(duration*fps),chunk=Math.ceil(totalFrames/jobs);
  const parts=await Promise.all(Array.from({length:jobs},async(_,job)=>{
   const begin=job*chunk,end=Math.min(begin+chunk,totalFrames);if(begin>=end)return null;
   const part=path.join(outDir,`part-${job}.mp4`);
   const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
   const browserErrors=[];page.on('pageerror',e=>browserErrors.push(e.message));
   await page.goto(url);await page.evaluate(()=>window.ready);
   const enc=spawn(ffmpeg,['-hide_banner','-loglevel','error','-y','-f','image2pipe','-framerate',String(fps),'-c:v','mjpeg','-i','pipe:0','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-threads','3','-movflags','+faststart',part],{stdio:['pipe','ignore','pipe']});
   let stderr='';enc.stderr.on('data',x=>{stderr=(stderr+x).slice(-5000)});
   const encoded=new Promise((resolve,reject)=>{enc.once('error',reject);enc.once('exit',code=>code===0?resolve():reject(new Error(stderr)));});
   for(let frame=begin;frame<end;frame++){
    await page.evaluate(t=>window.renderFrame(t),frame/fps);
    const jpeg=await page.screenshot({type:'jpeg',quality:96});
    if(!enc.stdin.write(jpeg))await once(enc.stdin,'drain');
    if((frame-begin)%150===0)console.log(`Worker ${job+1}: ${frame-begin}/${end-begin} frames`);
   }
   enc.stdin.end();await encoded;await page.close();
   if(browserErrors.length)throw new Error(browserErrors.join('\n'));
   console.log(`Worker ${job+1} complete: ${end-begin} frames`);return part;
  }));
  const concat=path.join(outDir,'concat.txt');fs.writeFileSync(concat,parts.filter(Boolean).map(p=>`file '${p.replace(/'/g,"'\\''")}'`).join('\n')+'\n');
  await run(ffmpeg,['-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',concat,'-i',master,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-ar','48000','-t',String(duration),'-movflags','+faststart',output]);
  const page=await browser.newPage({viewport:{width:1920,height:1080}});await page.goto(url);await page.evaluate(()=>window.ready);
  await page.evaluate(()=>window.renderFrame(85.7,{poster:true}));await page.screenshot({path:path.join(root,'site/assets/lps-bench-film-poster.jpg'),type:'jpeg',quality:94});await page.close();
  const storyboard=JSON.parse(fs.readFileSync(path.join(root,'scripts/video_storyboard.json'),'utf8'));
  for(const lang of ['en','zh']){
   const vtt='WEBVTT\n\n'+storyboard.captions.map((q,i)=>`${i+1}\n${stamp(q.start)} --> ${stamp(q.end)}\n${q[lang]}\n`).join('\n');
   fs.writeFileSync(path.join(root,`site/assets/lps-bench-film.${lang}.vtt`),vtt);
  }
  const metadata={title:storyboard.title,duration_seconds:duration,width,height,fps,video_codec:'H.264',audio_codec:'AAC',audio_sample_rate:48000,bytes:fs.statSync(output).size,rendering:'Deterministic Canvas motion design; original paper crops',narration:'Synthetic English narration',music:'Original procedural score',source:'scripts/video/',storyboard:'scripts/video_storyboard.json',paper_version:storyboard.paper_version,paper_url:storyboard.paper_url};
  fs.writeFileSync(path.join(root,'site/assets/lps-bench-film.json'),JSON.stringify(metadata,null,2)+'\n');
  console.log(`Complete: ${output} (${(metadata.bytes/1024/1024).toFixed(1)} MiB)`);
 }finally{await browser.close();server.close();}
}
main().catch(e=>{console.error(e);server.close();process.exitCode=1;});
