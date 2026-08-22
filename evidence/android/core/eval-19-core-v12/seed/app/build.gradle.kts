plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.kapt")
}

android {
    namespace = "dev.skyl.notes"
    compileSdk = 36
    defaultConfig {
        applicationId = "dev.skyl.notes"
        minSdk = 26
        targetSdk = 36
    }
    buildTypes {
        release {
            // shipped as-is so far
        }
    }
    buildFeatures { compose = true }
}

dependencies {
    implementation(project(":core-data"))
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation(platform("androidx.compose:compose-bom:2024.12.01"))
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui")

    implementation("com.google.dagger:hilt-android:2.52")
    kapt("com.google.dagger:hilt-compiler:2.52")
}
