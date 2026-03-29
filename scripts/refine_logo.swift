import CoreGraphics
import Foundation
import ImageIO
import UniformTypeIdentifiers

func clamp(_ value: Double) -> UInt8 {
    UInt8(max(0, min(255, Int(value.rounded()))))
}

guard CommandLine.arguments.count >= 3 else {
    fputs("Usage: refine_logo.swift <input> <output>\n", stderr)
    exit(1)
}

let inputURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])

guard let source = CGImageSourceCreateWithURL(inputURL as CFURL, nil),
      let image = CGImageSourceCreateImageAtIndex(source, 0, nil) else {
    fputs("Unable to load image.\n", stderr)
    exit(1)
}

let cropRect = CGRect(x: 144, y: 328, width: 480, height: 360)
guard let cropped = image.cropping(to: cropRect) else {
    fputs("Unable to crop image.\n", stderr)
    exit(1)
}

let width = cropped.width
let height = cropped.height
let bytesPerPixel = 4
let bytesPerRow = width * bytesPerPixel
let bitsPerComponent = 8

guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB),
      let context = CGContext(
        data: nil,
        width: width,
        height: height,
        bitsPerComponent: bitsPerComponent,
        bytesPerRow: bytesPerRow,
        space: colorSpace,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
      ) else {
    fputs("Unable to build bitmap context.\n", stderr)
    exit(1)
}

context.draw(cropped, in: CGRect(x: 0, y: 0, width: width, height: height))

guard let data = context.data else {
    fputs("Unable to access pixel data.\n", stderr)
    exit(1)
}

let pixels = data.bindMemory(to: UInt8.self, capacity: height * bytesPerRow)

for y in 0..<height {
    for x in 0..<width {
        let offset = y * bytesPerRow + x * bytesPerPixel
        var r = pixels[offset]
        var g = pixels[offset + 1]
        var b = pixels[offset + 2]
        var a = pixels[offset + 3]

        if r > 242 && g > 242 && b > 242 {
            a = 0
        } else {
            let rf = Double(r) / 255.0
            let gf = Double(g) / 255.0
            let bf = Double(b) / 255.0
            let luminance = 0.2126 * rf + 0.7152 * gf + 0.0722 * bf

            let saturation = 0.76
            let contrast = 1.08
            let brightness = -0.01

            var nr = luminance + (rf - luminance) * saturation
            var ng = luminance + (gf - luminance) * saturation
            var nb = luminance + (bf - luminance) * saturation

            nr = ((nr - 0.5) * contrast) + 0.5 + brightness
            ng = ((ng - 0.5) * contrast) + 0.5 + brightness
            nb = ((nb - 0.5) * contrast) + 0.5 + brightness

            if ng > nr && ng > nb {
                ng *= 0.88
            }
            if nb > nr && nb > ng {
                nb *= 0.96
            }

            r = clamp(nr * 255.0)
            g = clamp(ng * 255.0)
            b = clamp(nb * 255.0)
        }

        pixels[offset] = r
        pixels[offset + 1] = g
        pixels[offset + 2] = b
        pixels[offset + 3] = a
    }
}

guard let outputImage = context.makeImage(),
      let destination = CGImageDestinationCreateWithURL(
        outputURL as CFURL,
        UTType.png.identifier as CFString,
        1,
        nil
      ) else {
    fputs("Unable to create output image.\n", stderr)
    exit(1)
}

CGImageDestinationAddImage(destination, outputImage, nil)
if CGImageDestinationFinalize(destination) {
    print(outputURL.path)
} else {
    fputs("Unable to save PNG.\n", stderr)
    exit(1)
}
