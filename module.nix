{ pkgs, lib, config, ... }:

with lib;

let
  cfg = config.services.moderator;

  configFmt = pkgs.formats.yaml {};

  configFile = configFmt.generate "moderator.yaml" cfg.config;

  moderator = pkgs.callPackage "/root/moderator" {};

in {
  options = {
    services.moderator = {
      enable = mkEnableOption "moderator";

      config = mkOption {
        type = configFmt.type;
        default = {};
        description = "Configuration for moderator.";
      };

      privateConfigFile = mkOption {
        type = types.path;
        description = "Path to config file with tokens.";
      };

      domain = mkOption {
        type = types.str;
        description = "Domain to run moderator under.";
      };
    };
  };

  config = mkIf cfg.enable {
    systemd.services."moderator" = {
      description = "moderator bot";
      wantedBy = [ "multi-user.target" ];
      serviceConfig = {
        LoadCredential = "private_cfg:${cfg.privateConfigFile}";
        DynamicUser = true;
        RuntimeDirectory = "moderator";
      };
      script = ''
        ${pkgs.yaml-merge}/bin/yaml-merge ${moderator}/etc/moderator.yaml ${configFile} > /tmp/moderator.yaml
        ${pkgs.yaml-merge}/bin/yaml-merge /tmp/moderator.yaml "$CREDENTIALS_DIRECTORY/private_cfg" > /run/moderator/config.yaml
        exec ${moderator}/bin/moderator --config /run/moderator/config.yaml --unix /run/moderator/http.sock --domain ${cfg.domain}
      '';
    };

    services.nginx = {
        enable = true;

        virtualHosts."${cfg.domain}" = {
            forceSSL = true;
            enableACME = true;
            locations."/".proxyPass = "http://unix:/run/moderator/http.sock";
        };
    };
  };
}
