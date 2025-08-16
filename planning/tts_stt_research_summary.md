# TTS/STT Research Summary for Japanese Language Learning App

*Research Date: August 13, 2025*

## Executive Summary

After comprehensive research, we've identified the optimal open-source TTS/STT solutions for a Japanese language learning app with client-side processing.

## 🏆 Final Recommendations

### Speech-to-Text (STT): OpenAI Whisper
- **License**: MIT (completely free for commercial use)
- **Japanese Support**: Excellent
- **Recommended Model**: `tiny` (39M params) for mobile deployment
- **Resource Requirements**: ~1GB RAM, ~150MB storage
- **Integration**: Custom React Native bridge required

### Text-to-Speech (TTS): Coqui TTS (Piper Alternative)
- **Primary**: Coqui TTS ⓍTTS for quality
- **Mobile**: Piper TTS for lightweight deployment
- **License**: MPL-2.0 / MIT respectively
- **Resource Requirements**: ~1-4GB RAM depending on model
- **Japanese Quality**: Excellent natural speech

## Detailed Analysis

### STT Engine Comparison
| Engine | Japanese Quality | License | Size | Mobile Ready |
|--------|------------------|---------|------|--------------|
| Whisper tiny | ⭐⭐⭐⭐ | MIT | 150MB | ✅ Yes |
| Whisper base | ⭐⭐⭐⭐⭐ | MIT | 300MB | ⚠️ Heavy |
| Mozilla DeepSpeech | ⭐⭐ | MPL-2.0 | 200MB | ✅ Yes |
| SpeechRecognition API | ⭐⭐⭐ | Browser | 0MB | 🌐 Web only |

### TTS Engine Comparison  
| Engine | Japanese Quality | License | Size | Voice Cloning |
|--------|------------------|---------|------|---------------|
| Coqui TTS ⓍTTS | ⭐⭐⭐⭐⭐ | MPL-2.0 | 2GB | ✅ Yes |
| Piper TTS | ⭐⭐⭐ | MIT | 80MB | ❌ No |
| eSpeak-ng | ⭐⭐ | GPL-3.0 | 10MB | ❌ No |
| Browser Speech API | ⭐⭐⭐ | Browser | 0MB | ❌ No |

## Implementation Strategy

### Mobile App Configuration
```
React Native App (~300MB total)
├── Whisper tiny model (150MB)
├── Piper TTS Japanese (80MB) 
├── App code & assets (70MB)
└── Local sentence database (20MB)
```

### Resource Requirements by Device Tier
| Tier | RAM | Storage | Target Devices |
|------|-----|---------|----------------|
| Minimum | 4GB | 1GB free | Budget Android, older iOS |
| Recommended | 6GB | 2GB free | Mid-range devices |
| Optimal | 8GB+ | 3GB free | Flagship devices |

## Technical Integration Notes

### Whisper Integration Approaches
1. **React Native bridge** to native Whisper implementation
2. **ONNX Runtime** for cross-platform inference
3. **WebAssembly** for web companion app
4. **Custom native modules** with optimized models

### TTS Integration Approaches  
1. **Piper TTS** with React Native bridge (recommended for mobile)
2. **Coqui TTS** via custom integration (premium features)
3. **Native TTS APIs** as fallback options
4. **Web Speech API** for web version

## Cost Analysis

### Development Costs
- **One-time**: React Native bridges development (~2-4 weeks)
- **Ongoing**: $0 - all processing happens locally
- **Total**: Development time only, no recurring costs

### Operational Costs
- **Server**: $0 (client-side processing)
- **API**: $0 (open-source models)
- **Storage**: $0 (local device storage)
- **Bandwidth**: Minimal (app updates only)

## Next Steps

1. **Proof of Concept**: Test Whisper tiny integration in React Native
2. **TTS Testing**: Evaluate Piper TTS quality for Japanese learning
3. **Performance Testing**: Benchmark on target devices  
4. **Architecture Design**: Finalize app structure and data flow
5. **Development Setup**: Initialize React Native project with AI dependencies

## Risk Assessment

### Low Risk ✅
- Both technologies are mature and well-documented
- Strong community support and active development
- Proven Japanese language support

### Medium Risk ⚠️  
- Custom React Native bridges require native development skills
- App size (~300MB) may impact download rates
- Performance optimization needed for older devices

### Mitigation Strategies
- Start with simpler integrations (ONNX Runtime)
- Progressive model downloading to reduce initial app size
- Fallback to device native APIs when needed
- Performance testing on minimum spec devices

---
*This research forms the foundation for our Japanese language learning app's speech technology stack.*
