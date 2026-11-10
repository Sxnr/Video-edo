import {installWhisperCpp, downloadWhisperModel} from '@remotion/install-whisper-cpp';
import path from 'node:path';
const to = path.resolve('whisper.cpp');
const model = process.env.WHISPER_MODEL || 'large-v3-turbo';
await installWhisperCpp({to, version: '1.7.4'});
await downloadWhisperModel({model, folder: to});
console.log('ok', model);
